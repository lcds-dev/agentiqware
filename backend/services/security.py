# =====================================
# Sistema de Seguridad Avanzado para Agentiqware
# =====================================

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import base64
import re

# Autenticación y Seguridad
from passlib.context import CryptContext
from passlib.totp import TOTP
import pyotp
from jose import JWTError, jwt, jwk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# OAuth y SSO
from authlib.integrations.flask_client import OAuth
import requests
from flask import Flask, request, session, redirect
import ldap3

# Rate Limiting y Protección
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Auditoría y Compliance
from google.cloud import logging as cloud_logging
from google.cloud import dlp_v2
from google.cloud import kms

# Base de datos
from google.cloud import firestore
import asyncio

# =====================================
# Configuración de Seguridad
# =====================================

class SecurityConfig:
    """Configuración de seguridad centralizada"""
    
    # JWT Configuration
    JWT_SECRET_KEY = secrets.token_urlsafe(32)
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Password Policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_HISTORY_COUNT = 5
    PASSWORD_MAX_AGE_DAYS = 90
    
    # MFA Settings
    MFA_REQUIRED_FOR_ADMIN = True
    MFA_TOTP_ISSUER = "Agentiqware"
    MFA_BACKUP_CODES_COUNT = 10
    
    # Session Security
    SESSION_TIMEOUT_MINUTES = 30
    SESSION_MAX_CONCURRENT = 3
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    RATE_LIMIT_LOGIN_ATTEMPTS = 5
    RATE_LIMIT_LOCKOUT_DURATION = 900  # 15 minutes
    
    # IP Security
    IP_WHITELIST_ENABLED = False
    IP_WHITELIST = []
    IP_BLACKLIST = []
    GEO_BLOCKING_ENABLED = False
    BLOCKED_COUNTRIES = []
    
    # Encryption
    ENCRYPTION_KEY = Fernet.generate_key()
    DATA_RETENTION_DAYS = 90
    
    # Audit
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_SENSITIVE_ACTIONS = True
    AUDIT_LOG_RETENTION_DAYS = 365

# =====================================
# Sistema de Autenticación Avanzado
# =====================================

class AuthenticationManager:
    """Gestor de autenticación con múltiples métodos"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["argon2", "bcrypt"],
            deprecated="auto",
            argon2__memory_cost=65536,
            argon2__time_cost=3,
            argon2__parallelism=4
        )
        self.db = firestore.Client()
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.cipher_suite = Fernet(SecurityConfig.ENCRYPTION_KEY)
        
    async def register_user(
        self,
        email: str,
        password: str,
        name: str,
        organization: Optional[str] = None,
        require_mfa: bool = False
    ) -> Dict[str, Any]:
        """
        Registrar nuevo usuario con validaciones de seguridad
        
        Args:
            email: Email del usuario
            password: Contraseña
            name: Nombre completo
            organization: Organización (opcional)
            require_mfa: Si requiere MFA
            
        Returns:
            Información del usuario creado
        """
        # Validar email
        if not self._validate_email(email):
            raise ValueError("Invalid email format")
        
        # Verificar si el usuario existe
        existing = self.db.collection('users').where('email', '==', email).get()
        if existing:
            raise ValueError("User already exists")
        
        # Validar fortaleza de contraseña
        password_validation = self._validate_password_strength(password)
        if not password_validation['valid']:
            raise ValueError(f"Password validation failed: {password_validation['errors']}")
        
        # Hash de contraseña
        password_hash = self.pwd_context.hash(password)
        
        # Generar user ID
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        
        # Generar salt único para el usuario
        salt = secrets.token_hex(32)
        
        # Preparar datos del usuario
        user_data = {
            'user_id': user_id,
            'email': email,
            'email_normalized': email.lower(),
            'name': name,
            'organization': organization,
            'password_hash': password_hash,
            'password_history': [password_hash],
            'salt': salt,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'last_password_change': datetime.utcnow().isoformat(),
            'status': 'active',
            'email_verified': False,
            'mfa_enabled': require_mfa,
            'mfa_secret': None,
            'backup_codes': [],
            'failed_login_attempts': 0,
            'last_failed_login': None,
            'account_locked_until': None,
            'security_questions': [],
            'trusted_devices': [],
            'login_history': [],
            'api_keys': [],
            'permissions': ['user'],
            'data_encryption_key': self._generate_user_encryption_key()
        }
        
        # Si requiere MFA, generar secreto
        if require_mfa:
            mfa_secret = pyotp.random_base32()
            user_data['mfa_secret'] = self._encrypt_sensitive_data(mfa_secret)
            user_data['backup_codes'] = self._generate_backup_codes()
        
        # Guardar en base de datos
        self.db.collection('users').document(user_id).set(user_data)
        
        # Generar token de verificación de email
        verification_token = self._generate_verification_token(user_id)
        
        # Registrar evento de auditoría
        await self._audit_log('user_registration', user_id, {
            'email': email,
            'organization': organization,
            'mfa_enabled': require_mfa
        })
        
        # Enviar email de verificación
        await self._send_verification_email(email, verification_token)
        
        return {
            'user_id': user_id,
            'email': email,
            'verification_required': True,
            'mfa_enabled': require_mfa,
            'mfa_qr_code': self._generate_mfa_qr_code(email, mfa_secret) if require_mfa else None
        }
    
    async def authenticate(
        self,
        email: str,
        password: str,
        mfa_code: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Autenticar usuario con múltiples factores
        
        Args:
            email: Email del usuario
            password: Contraseña
            mfa_code: Código MFA (si está habilitado)
            device_id: ID del dispositivo
            ip_address: Dirección IP
            
        Returns:
            Tokens de autenticación
        """
        # Verificar rate limiting
        if not await self._check_rate_limit(email, ip_address):
            raise Exception("Too many login attempts. Please try again later.")
        
        # Buscar usuario
        users = self.db.collection('users').where('email_normalized', '==', email.lower()).get()
        
        if not users:
            await self._record_failed_login(email, ip_address)
            raise ValueError("Invalid credentials")
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        user_id = user_data['user_id']
        
        # Verificar si la cuenta está bloqueada
        if user_data.get('account_locked_until'):
            locked_until = datetime.fromisoformat(user_data['account_locked_until'])
            if datetime.utcnow() < locked_until:
                raise Exception(f"Account locked until {locked_until}")
        
        # Verificar contraseña
        if not self.pwd_context.verify(password, user_data['password_hash']):
            await self._record_failed_login(email, ip_address, user_id)
            raise ValueError("Invalid credentials")
        
        # Verificar MFA si está habilitado
        if user_data.get('mfa_enabled'):
            if not mfa_code:
                return {
                    'status': 'mfa_required',
                    'user_id': user_id,
                    'session_token': self._generate_temp_session_token(user_id)
                }
            
            if not await self._verify_mfa_code(user_id, mfa_code):
                await self._record_failed_login(email, ip_address, user_id, 'mfa_failed')
                raise ValueError("Invalid MFA code")
        
        # Verificar dispositivo confiable
        if device_id and device_id not in user_data.get('trusted_devices', []):
            # Enviar notificación de nuevo dispositivo
            await self._notify_new_device_login(user_id, device_id, ip_address)
        
        # Generar tokens
        access_token = self._generate_access_token(user_id, user_data['permissions'])
        refresh_token = self._generate_refresh_token(user_id)
        
        # Actualizar información de login
        login_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'device_id': device_id,
            'success': True
        }
        
        # Agregar a historial de login
        login_history = user_data.get('login_history', [])
        login_history.insert(0, login_record)
        login_history = login_history[:100]  # Mantener últimos 100 logins
        
        # Actualizar usuario
        self.db.collection('users').document(user_id).update({
            'last_login': datetime.utcnow().isoformat(),
            'failed_login_attempts': 0,
            'login_history': login_history
        })
        
        # Crear sesión
        session_id = await self._create_session(user_id, device_id, ip_address)
        
        # Auditoría
        await self._audit_log('user_login', user_id, {
            'ip_address': ip_address,
            'device_id': device_id,
            'mfa_used': user_data.get('mfa_enabled', False)
        })
        
        return {
            'status': 'success',
            'user_id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_id': session_id,
            'expires_in': SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES.total_seconds()
        }
    
    async def enable_mfa(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Habilitar MFA para un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Configuración MFA
        """
        # Generar secreto MFA
        secret = pyotp.random_base32()
        
        # Generar códigos de respaldo
        backup_codes = self._generate_backup_codes()
        
        # Actualizar usuario
        self.db.collection('users').document(user_id).update({
            'mfa_enabled': True,
            'mfa_secret': self._encrypt_sensitive_data(secret),
            'backup_codes': backup_codes,
            'mfa_enabled_at': datetime.utcnow().isoformat()
        })
        
        # Obtener email del usuario
        user_doc = self.db.collection('users').document(user_id).get()
        email = user_doc.to_dict()['email']
        
        # Auditoría
        await self._audit_log('mfa_enabled', user_id, {})
        
        return {
            'secret': secret,
            'qr_code': self._generate_mfa_qr_code(email, secret),
            'backup_codes': backup_codes
        }
    
    async def verify_api_key(
        self,
        api_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verificar API key
        
        Args:
            api_key: API key a verificar
            
        Returns:
            Información del usuario si es válida
        """
        # Buscar en cache primero
        cached = self.redis_client.get(f"api_key:{api_key}")
        if cached:
            return json.loads(cached)
        
        # Hash del API key para búsqueda
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Buscar en base de datos
        api_keys = self.db.collection('api_keys').where('key_hash', '==', key_hash).get()
        
        if not api_keys:
            return None
        
        key_doc = api_keys[0]
        key_data = key_doc.to_dict()
        
        # Verificar expiración
        if key_data.get('expires_at'):
            expires = datetime.fromisoformat(key_data['expires_at'])
            if datetime.utcnow() > expires:
                return None
        
        # Verificar límites de uso
        if key_data.get('usage_limit'):
            if key_data.get('usage_count', 0) >= key_data['usage_limit']:
                return None
        
        # Incrementar contador de uso
        self.db.collection('api_keys').document(key_doc.id).update({
            'usage_count': key_data.get('usage_count', 0) + 1,
            'last_used': datetime.utcnow().isoformat()
        })
        
        # Obtener información del usuario
        user_doc = self.db.collection('users').document(key_data['user_id']).get()
        user_data = user_doc.to_dict()
        
        result = {
            'user_id': key_data['user_id'],
            'permissions': user_data['permissions'],
            'rate_limit': key_data.get('rate_limit', 1000)
        }
        
        # Cachear resultado
        self.redis_client.setex(
            f"api_key:{api_key}",
            300,  # 5 minutos
            json.dumps(result)
        )
        
        return result
    
    # Métodos auxiliares privados
    
    def _validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validar fortaleza de contraseña"""
        errors = []
        
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters")
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        
        if SecurityConfig.PASSWORD_REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain digits")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special characters")
        
        # Verificar contraseñas comunes
        common_passwords = ['password', '123456', 'qwerty', 'admin']
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calcular puntuación de fortaleza (0-100)"""
        score = 0
        
        # Longitud
        score += min(password.__len__() * 4, 40)
        
        # Variedad de caracteres
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 20
        
        # Entropía
        unique_chars = len(set(password))
        score += min(unique_chars * 2, 10)
        
        return min(score, 100)
    
    def _generate_user_encryption_key(self) -> str:
        """Generar clave de encriptación única para usuario"""
        return Fernet.generate_key().decode()
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encriptar datos sensibles"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Desencriptar datos sensibles"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def _generate_backup_codes(self) -> List[str]:
        """Generar códigos de respaldo para MFA"""
        codes = []
        for _ in range(SecurityConfig.MFA_BACKUP_CODES_COUNT):
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(hashlib.sha256(formatted_code.encode()).hexdigest())
        return codes
    
    def _generate_mfa_qr_code(self, email: str, secret: str) -> str:
        """Generar código QR para MFA"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=SecurityConfig.MFA_TOTP_ISSUER
        )
        # Aquí se generaría el QR real
        return totp_uri
    
    def _generate_verification_token(self, user_id: str) -> str:
        """Generar token de verificación de email"""
        token = secrets.token_urlsafe(32)
        
        # Guardar en Redis con expiración
        self.redis_client.setex(
            f"verify:{token}",
            86400,  # 24 horas
            user_id
        )
        
        return token
    
    def _generate_temp_session_token(self, user_id: str) -> str:
        """Generar token temporal de sesión para MFA"""
        token = secrets.token_urlsafe(32)
        
        # Guardar en Redis con expiración corta
        self.redis_client.setex(
            f"temp_session:{token}",
            300,  # 5 minutos
            user_id
        )
        
        return token
    
    def _generate_access_token(self, user_id: str, permissions: List[str]) -> str:
        """Generar JWT access token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'type': 'access',
            'exp': datetime.utcnow() + SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES,
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())
        }
        
        return jwt.encode(payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
    
    def _generate_refresh_token(self, user_id: str) -> str:
        """Generar JWT refresh token"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES,
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())
        }
        
        token = jwt.encode(payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
        
        # Guardar en base de datos
        self.db.collection('refresh_tokens').add({
            'token_id': payload['jti'],
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES).isoformat(),
            'revoked': False
        })
        
        return token
    
    async def _check_rate_limit(self, email: str, ip_address: str) -> bool:
        """Verificar límite de intentos de login"""
        key = f"login_attempts:{email}:{ip_address}"
        attempts = self.redis_client.get(key)
        
        if attempts and int(attempts) >= SecurityConfig.RATE_LIMIT_LOGIN_ATTEMPTS:
            return False
        
        return True
    
    async def _record_failed_login(
        self,
        email: str,
        ip_address: str,
        user_id: Optional[str] = None,
        reason: str = 'invalid_credentials'
    ):
        """Registrar intento de login fallido"""
        # Incrementar contador en Redis
        key = f"login_attempts:{email}:{ip_address}"
        self.redis_client.incr(key)
        self.redis_client.expire(key, SecurityConfig.RATE_LIMIT_LOCKOUT_DURATION)
        
        # Si tenemos user_id, actualizar en base de datos
        if user_id:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            user_data = user_doc.to_dict()
            
            failed_attempts = user_data.get('failed_login_attempts', 0) + 1
            
            update_data = {
                'failed_login_attempts': failed_attempts,
                'last_failed_login': datetime.utcnow().isoformat()
            }
            
            # Bloquear cuenta si se exceden los intentos
            if failed_attempts >= SecurityConfig.RATE_LIMIT_LOGIN_ATTEMPTS:
                update_data['account_locked_until'] = (
                    datetime.utcnow() + timedelta(seconds=SecurityConfig.RATE_LIMIT_LOCKOUT_DURATION)
                ).isoformat()
            
            user_ref.update(update_data)
        
        # Auditoría
        await self._audit_log('failed_login', user_id or 'unknown', {
            'email': email,
            'ip_address': ip_address,
            'reason': reason
        })
    
    async def _verify_mfa_code(self, user_id: str, code: str) -> bool:
        """Verificar código MFA"""
        user_doc = self.db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        
        # Verificar código TOTP
        encrypted_secret = user_data.get('mfa_secret')
        if encrypted_secret:
            secret = self._decrypt_sensitive_data(encrypted_secret)
            totp = pyotp.TOTP(secret)
            
            if totp.verify(code, valid_window=1):
                return True
        
        # Verificar códigos de respaldo
        backup_codes = user_data.get('backup_codes', [])
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash in backup_codes:
            # Remover código usado
            backup_codes.remove(code_hash)
            self.db.collection('users').document(user_id).update({
                'backup_codes': backup_codes
            })
            return True
        
        return False
    
    async def _create_session(
        self,
        user_id: str,
        device_id: Optional[str],
        ip_address: Optional[str]
    ) -> str:
        """Crear sesión de usuario"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'device_id': device_id,
            'ip_address': ip_address,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES)).isoformat(),
            'active': True
        }
        
        # Guardar en Redis para acceso rápido
        self.redis_client.setex(
            f"session:{session_id}",
            SecurityConfig.SESSION_TIMEOUT_MINUTES * 60,
            json.dumps(session_data)
        )
        
        # También guardar en Firestore para persistencia
        self.db.collection('sessions').document(session_id).set(session_data)
        
        return session_id
    
    async def _notify_new_device_login(
        self,
        user_id: str,
        device_id: str,
        ip_address: str
    ):
        """Notificar login desde nuevo dispositivo"""
        # Implementar notificación por email/SMS
        pass
    
    async def _send_verification_email(self, email: str, token: str):
        """Enviar email de verificación"""
        # Implementar envío de email
        pass
    
    async def _audit_log(
        self,
        action: str,
        user_id: str,
        details: Dict[str, Any]
    ):
        """Registrar evento de auditoría"""
        if not SecurityConfig.AUDIT_LOG_ENABLED:
            return
        
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details,
            'ip_address': details.get('ip_address'),
            'user_agent': details.get('user_agent'),
            'session_id': details.get('session_id')
        }
        
        # Guardar en Firestore
        self.db.collection('audit_logs').add(audit_entry)
        
        # También enviar a Cloud Logging
        logger = cloud_logging.Client().logger('security-audit')
        logger.log_struct(audit_entry, severity='INFO')

# =====================================
# SSO y OAuth Integration
# =====================================

class SSOManager:
    """Gestor de Single Sign-On"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.oauth = OAuth(app)
        self.configure_providers()
    
    def configure_providers(self):
        """Configurar proveedores OAuth"""
        
        # Google OAuth
        self.google = self.oauth.register(
            name='google',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        
        # Microsoft Azure AD
        self.microsoft = self.oauth.register(
            name='microsoft',
            client_id=os.environ.get('AZURE_CLIENT_ID'),
            client_secret=os.environ.get('AZURE_CLIENT_SECRET'),
            api_base_url='https://graph.microsoft.com/v1.0/',
            request_token_url=None,
            access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
            authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            client_kwargs={
                'scope': 'User.Read'
            }
        )
        
        # GitHub OAuth
        self.github = self.oauth.register(
            name='github',
            client_id=os.environ.get('GITHUB_CLIENT_ID'),
            client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'}
        )
    
    async def handle_sso_callback(
        self,
        provider: str,
        code: str
    ) -> Dict[str, Any]:
        """
        Manejar callback de SSO
        
        Args:
            provider: Proveedor OAuth (google, microsoft, github)
            code: Código de autorización
            
        Returns:
            Información del usuario autenticado
        """
        if provider == 'google':
            token = await self.google.authorize_access_token()
            user_info = token.get('userinfo')
            
        elif provider == 'microsoft':
            token = await self.microsoft.authorize_access_token()
            resp = await self.microsoft.get('me')
            user_info = resp.json()
            
        elif provider == 'github':
            token = await self.github.authorize_access_token()
            resp = await self.github.get('user')
            user_info = resp.json()
            
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Buscar o crear usuario
        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('login')
        
        db = firestore.Client()
        users = db.collection('users').where('email', '==', email).get()
        
        if users:
            # Usuario existe, actualizar último login
            user_doc = users[0]
            user_id = user_doc.to_dict()['user_id']
            
            db.collection('users').document(user_id).update({
                'last_login': datetime.utcnow().isoformat(),
                'last_sso_provider': provider
            })
        else:
            # Crear nuevo usuario
            user_id = f"usr_{uuid.uuid4().hex[:12]}"
            
            db.collection('users').document(user_id).set({
                'user_id': user_id,
                'email': email,
                'name': name,
                'created_at': datetime.utcnow().isoformat(),
                'sso_provider': provider,
                'sso_id': user_info.get('id') or user_info.get('sub'),
                'email_verified': True,  # SSO providers verify email
                'status': 'active'
            })
        
        # Generar tokens
        auth_manager = AuthenticationManager()
        access_token = auth_manager._generate_access_token(user_id, ['user'])
        refresh_token = auth_manager._generate_refresh_token(user_id)
        
        return {
            'user_id': user_id,
            'email': email,
            'name': name,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'provider': provider
        }

# =====================================
# LDAP/Active Directory Integration
# =====================================

class LDAPAuthenticator:
    """Autenticador LDAP/Active Directory"""
    
    def __init__(
        self,
        server_url: str,
        base_dn: str,
        bind_dn: Optional[str] = None,
        bind_password: Optional[str] = None
    ):
        self.server_url = server_url
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Autenticar usuario contra LDAP
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Información del usuario si la autenticación es exitosa
        """
        server = ldap3.Server(self.server_url, get_info=ldap3.ALL)
        
        # Construir DN del usuario
        user_dn = f"uid={username},{self.base_dn}"
        
        try:
            # Intentar bind con credenciales del usuario
            conn = ldap3.Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            # Buscar información del usuario
            conn.search(
                search_base=self.base_dn,
                search_filter=f'(uid={username})',
                attributes=['cn', 'mail', 'memberOf']
            )
            
            if conn.entries:
                user_entry = conn.entries[0]
                
                user_info = {
                    'username': username,
                    'name': str(user_entry.cn),
                    'email': str(user_entry.mail) if hasattr(user_entry, 'mail') else None,
                    'groups': [str(group) for group in user_entry.memberOf] if hasattr(user_entry, 'memberOf') else [],
                    'dn': user_dn
                }
                
                conn.unbind()
                return user_info
                
        except ldap3.core.exceptions.LDAPBindError:
            # Credenciales inválidas
            pass
        except Exception as e:
            print(f"LDAP error: {e}")
        
        return None
    
    async def sync_users(self) -> List[Dict[str, Any]]:
        """
        Sincronizar usuarios desde LDAP
        
        Returns:
            Lista de usuarios sincronizados
        """
        server = ldap3.Server(self.server_url, get_info=ldap3.ALL)
        
        # Conectar con cuenta de servicio
        conn = ldap3.Connection(
            server,
            user=self.bind_dn,
            password=self.bind_password,
            auto_bind=True
        )
        
        # Buscar todos los usuarios
        conn.search(
            search_base=self.base_dn,
            search_filter='(objectClass=person)',
            attributes=['uid', 'cn', 'mail', 'memberOf']
        )
        
        users = []
        for entry in conn.entries:
            users.append({
                'username': str(entry.uid),
                'name': str(entry.cn),
                'email': str(entry.mail) if hasattr(entry, 'mail') else None,
                'groups': [str(group) for group in entry.memberOf] if hasattr(entry, 'memberOf') else []
            })
        
        conn.unbind()
        return users

# =====================================
# Data Loss Prevention (DLP)
# =====================================

class DLPManager:
    """Gestor de prevención de pérdida de datos"""
    
    def __init__(self):
        self.dlp_client = dlp_v2.DlpServiceClient()
        self.project = os.environ.get('GCP_PROJECT_ID')
        
    async def inspect_content(
        self,
        content: str,
        info_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Inspeccionar contenido en busca de datos sensibles
        
        Args:
            content: Contenido a inspeccionar
            info_types: Tipos de información a buscar
            
        Returns:
            Resultados de la inspección
        """
        if not info_types:
            info_types = [
                'CREDIT_CARD_NUMBER',
                'EMAIL_ADDRESS',
                'PHONE_NUMBER',
                'PERSON_NAME',
                'PASSPORT',
                'DRIVER_LICENSE_NUMBER',
                'SOCIAL_SECURITY_NUMBER'
            ]
        
        # Configurar tipos de información
        info_types_config = [
            {'name': info_type} for info_type in info_types
        ]
        
        # Configurar solicitud de inspección
        inspect_config = {
            'info_types': info_types_config,
            'min_likelihood': dlp_v2.Likelihood.POSSIBLE,
            'include_quote': True,
            'limits': {
                'max_findings_per_request': 100
            }
        }
        
        # Crear ítem a inspeccionar
        item = {'value': content}
        
        # Ejecutar inspección
        parent = f"projects/{self.project}/locations/global"
        response = self.dlp_client.inspect_content(
            request={
                'parent': parent,
                'inspect_config': inspect_config,
                'item': item
            }
        )
        
        # Procesar resultados
        findings = []
        for finding in response.result.findings:
            findings.append({
                'type': finding.info_type.name,
                'likelihood': finding.likelihood.name,
                'quote': finding.quote,
                'location': {
                    'start': finding.location.byte_range.start,
                    'end': finding.location.byte_range.end
                }
            })
        
        return {
            'has_sensitive_data': len(findings) > 0,
            'findings': findings,
            'risk_score': self._calculate_risk_score(findings)
        }
    
    async def redact_content(
        self,
        content: str,
        info_types: Optional[List[str]] = None
    ) -> str:
        """
        Redactar información sensible del contenido
        
        Args:
            content: Contenido a redactar
            info_types: Tipos de información a redactar
            
        Returns:
            Contenido redactado
        """
        if not info_types:
            info_types = ['CREDIT_CARD_NUMBER', 'EMAIL_ADDRESS', 'PHONE_NUMBER']
        
        # Configurar redacción
        deidentify_config = {
            'info_type_transformations': {
                'transformations': [
                    {
                        'info_types': [{'name': info_type} for info_type in info_types],
                        'primitive_transformation': {
                            'replace_config': {
                                'new_value': {'string_value': '[REDACTED]'}
                            }
                        }
                    }
                ]
            }
        }
        
        # Ejecutar redacción
        parent = f"projects/{self.project}/locations/global"
        response = self.dlp_client.deidentify_content(
            request={
                'parent': parent,
                'deidentify_config': deidentify_config,
                'item': {'value': content}
            }
        )
        
        return response.item.value
    
    def _calculate_risk_score(self, findings: List[Dict]) -> int:
        """Calcular puntuación de riesgo"""
        if not findings:
            return 0
        
        score = 0
        high_risk_types = ['CREDIT_CARD_NUMBER', 'SOCIAL_SECURITY_NUMBER', 'PASSPORT']
        
        for finding in findings:
            if finding['type'] in high_risk_types:
                score += 10
            else:
                score += 5
            
            # Ajustar por probabilidad
            if finding['likelihood'] == 'VERY_LIKELY':
                score += 3
            elif finding['likelihood'] == 'LIKELY':
                score += 2
            elif finding['likelihood'] == 'POSSIBLE':
                score += 1
        
        return min(score, 100)