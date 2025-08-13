# =====================================
# Sistema de Internacionalización (i18n) para Backend
# =====================================

from typing import Dict, Any, Optional
from enum import Enum
import json

class Language(Enum):
    """Idiomas soportados"""
    EN = "en"
    ES = "es"

class TranslationManager:
    """Gestor de traducciones para el backend"""
    
    translations = {
        "en": {
            # Authentication messages
            "auth.login_success": "Login successful",
            "auth.login_failed": "Invalid credentials",
            "auth.user_exists": "User already exists",
            "auth.user_created": "User created successfully",
            "auth.token_expired": "Authentication token has expired",
            "auth.token_invalid": "Invalid authentication token",
            "auth.unauthorized": "Unauthorized access",
            
            # Flow messages
            "flow.created": "Flow created successfully",
            "flow.updated": "Flow updated successfully",
            "flow.deleted": "Flow deleted successfully",
            "flow.not_found": "Flow not found",
            "flow.execution_started": "Flow execution started",
            "flow.execution_completed": "Flow execution completed successfully",
            "flow.execution_failed": "Flow execution failed",
            "flow.saved": "Flow saved successfully",
            "flow.restored": "Flow restored from version {version}",
            "flow.scheduled": "Flow scheduled successfully",
            
            # Component messages
            "component.created": "Component created successfully",
            "component.updated": "Component updated successfully",
            "component.deleted": "Component deleted successfully",
            "component.not_found": "Component not found",
            "component.invalid_type": "Invalid component type",
            
            # Execution messages
            "execution.started": "Execution started",
            "execution.completed": "Execution completed",
            "execution.failed": "Execution failed: {error}",
            "execution.node_executed": "Node {node_id} executed successfully",
            "execution.node_failed": "Node {node_id} execution failed",
            "execution.timeout": "Execution timeout exceeded",
            
            # File operations
            "file.not_found": "File not found: {filename}",
            "file.uploaded": "File uploaded successfully",
            "file.deleted": "File deleted successfully",
            "file.invalid_format": "Invalid file format",
            "file.too_large": "File size exceeds limit",
            
            # Data processing
            "data.invalid_format": "Invalid data format",
            "data.processing_error": "Error processing data: {error}",
            "data.merge_success": "Data merged successfully",
            "data.export_success": "Data exported successfully",
            
            # Validation messages
            "validation.required_field": "Field '{field}' is required",
            "validation.invalid_email": "Invalid email format",
            "validation.password_weak": "Password must be at least 8 characters",
            "validation.invalid_format": "Invalid format for field '{field}'",
            "validation.max_length": "Field '{field}' exceeds maximum length",
            
            # AI messages
            "ai.generation_started": "AI flow generation started",
            "ai.generation_completed": "AI flow generated successfully",
            "ai.generation_failed": "AI generation failed",
            "ai.prompt_too_long": "Prompt exceeds maximum length",
            "ai.invalid_prompt": "Invalid or unclear prompt",
            
            # Subscription messages
            "subscription.limit_reached": "You have reached your plan limit for {resource}",
            "subscription.upgrade_required": "Please upgrade your plan to access this feature",
            "subscription.payment_failed": "Payment processing failed",
            "subscription.renewed": "Subscription renewed successfully",
            
            # System messages
            "system.maintenance": "System under maintenance",
            "system.error": "An unexpected error occurred",
            "system.rate_limit": "Rate limit exceeded. Please try again later",
            "system.service_unavailable": "Service temporarily unavailable",
            
            # Success messages
            "success.saved": "Changes saved successfully",
            "success.deleted": "Deleted successfully",
            "success.updated": "Updated successfully",
            "success.operation": "Operation completed successfully"
        },
        
        "es": {
            # Mensajes de autenticación
            "auth.login_success": "Inicio de sesión exitoso",
            "auth.login_failed": "Credenciales inválidas",
            "auth.user_exists": "El usuario ya existe",
            "auth.user_created": "Usuario creado exitosamente",
            "auth.token_expired": "El token de autenticación ha expirado",
            "auth.token_invalid": "Token de autenticación inválido",
            "auth.unauthorized": "Acceso no autorizado",
            
            # Mensajes de flujos
            "flow.created": "Flujo creado exitosamente",
            "flow.updated": "Flujo actualizado exitosamente",
            "flow.deleted": "Flujo eliminado exitosamente",
            "flow.not_found": "Flujo no encontrado",
            "flow.execution_started": "Ejecución del flujo iniciada",
            "flow.execution_completed": "Ejecución del flujo completada exitosamente",
            "flow.execution_failed": "La ejecución del flujo falló",
            "flow.saved": "Flujo guardado exitosamente",
            "flow.restored": "Flujo restaurado desde la versión {version}",
            "flow.scheduled": "Flujo programado exitosamente",
            
            # Mensajes de componentes
            "component.created": "Componente creado exitosamente",
            "component.updated": "Componente actualizado exitosamente",
            "component.deleted": "Componente eliminado exitosamente",
            "component.not_found": "Componente no encontrado",
            "component.invalid_type": "Tipo de componente inválido",
            
            # Mensajes de ejecución
            "execution.started": "Ejecución iniciada",
            "execution.completed": "Ejecución completada",
            "execution.failed": "Ejecución fallida: {error}",
            "execution.node_executed": "Nodo {node_id} ejecutado exitosamente",
            "execution.node_failed": "La ejecución del nodo {node_id} falló",
            "execution.timeout": "Tiempo de ejecución excedido",
            
            # Operaciones de archivo
            "file.not_found": "Archivo no encontrado: {filename}",
            "file.uploaded": "Archivo cargado exitosamente",
            "file.deleted": "Archivo eliminado exitosamente",
            "file.invalid_format": "Formato de archivo inválido",
            "file.too_large": "El tamaño del archivo excede el límite",
            
            # Procesamiento de datos
            "data.invalid_format": "Formato de datos inválido",
            "data.processing_error": "Error procesando datos: {error}",
            "data.merge_success": "Datos combinados exitosamente",
            "data.export_success": "Datos exportados exitosamente",
            
            # Mensajes de validación
            "validation.required_field": "El campo '{field}' es requerido",
            "validation.invalid_email": "Formato de email inválido",
            "validation.password_weak": "La contraseña debe tener al menos 8 caracteres",
            "validation.invalid_format": "Formato inválido para el campo '{field}'",
            "validation.max_length": "El campo '{field}' excede la longitud máxima",
            
            # Mensajes de IA
            "ai.generation_started": "Generación de flujo con IA iniciada",
            "ai.generation_completed": "Flujo generado con IA exitosamente",
            "ai.generation_failed": "La generación con IA falló",
            "ai.prompt_too_long": "El prompt excede la longitud máxima",
            "ai.invalid_prompt": "Prompt inválido o poco claro",
            
            # Mensajes de suscripción
            "subscription.limit_reached": "Has alcanzado el límite de tu plan para {resource}",
            "subscription.upgrade_required": "Por favor actualiza tu plan para acceder a esta función",
            "subscription.payment_failed": "El procesamiento del pago falló",
            "subscription.renewed": "Suscripción renovada exitosamente",
            
            # Mensajes del sistema
            "system.maintenance": "Sistema en mantenimiento",
            "system.error": "Ocurrió un error inesperado",
            "system.rate_limit": "Límite de solicitudes excedido. Por favor intenta más tarde",
            "system.service_unavailable": "Servicio temporalmente no disponible",
            
            # Mensajes de éxito
            "success.saved": "Cambios guardados exitosamente",
            "success.deleted": "Eliminado exitosamente",
            "success.updated": "Actualizado exitosamente",
            "success.operation": "Operación completada exitosamente"
        }
    }
    
    @classmethod
    def get_message(cls, key: str, lang: str = "en", **kwargs) -> str:
        """
        Obtener un mensaje traducido
        
        Args:
            key: Clave del mensaje
            lang: Código del idioma (en/es)
            **kwargs: Parámetros para formatear el mensaje
        
        Returns:
            Mensaje traducido y formateado
        """
        if lang not in cls.translations:
            lang = "en"
        
        message = cls.translations[lang].get(key, key)
        
        # Formatear el mensaje con los parámetros proporcionados
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError:
                pass
        
        return message
    
    @classmethod
    def get_language_from_request(cls, request) -> str:
        """
        Detectar el idioma desde la solicitud HTTP
        
        Args:
            request: Objeto de solicitud HTTP
        
        Returns:
            Código del idioma detectado
        """
        # Primero intentar obtener del header Accept-Language
        accept_language = request.headers.get('Accept-Language', '')
        if accept_language:
            # Parsear el header Accept-Language
            languages = accept_language.split(',')
            for lang in languages:
                lang_code = lang.split(';')[0].strip()[:2].lower()
                if lang_code in ['en', 'es']:
                    return lang_code
        
        # Luego intentar obtener del parámetro de consulta
        lang_param = request.args.get('lang', '').lower()
        if lang_param in ['en', 'es']:
            return lang_param
        
        # Finalmente, usar el idioma por defecto
        return 'en'

# =====================================
# Decorador para respuestas multiidioma
# =====================================

from functools import wraps
from flask import request, jsonify

def with_i18n(func):
    """
    Decorador para agregar soporte de internacionalización a las funciones
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Detectar idioma de la solicitud
        lang = TranslationManager.get_language_from_request(request)
        
        # Agregar el idioma al contexto
        kwargs['lang'] = lang
        
        # Ejecutar la función
        result = func(*args, **kwargs)
        
        # Si el resultado es una tupla (response, status_code)
        if isinstance(result, tuple):
            response_data, status_code = result
            
            # Agregar el idioma a la respuesta
            if isinstance(response_data, dict):
                response_data['lang'] = lang
            
            return response_data, status_code
        
        return result
    
    return wrapper

# =====================================
# Respuestas estandarizadas con i18n
# =====================================

class ApiResponse:
    """Clase para generar respuestas API estandarizadas con i18n"""
    
    @staticmethod
    def success(message_key: str, data: Any = None, lang: str = "en", **kwargs) -> Dict:
        """
        Generar respuesta de éxito
        
        Args:
            message_key: Clave del mensaje de traducción
            data: Datos a incluir en la respuesta
            lang: Idioma de la respuesta
            **kwargs: Parámetros para el mensaje
        
        Returns:
            Diccionario de respuesta
        """
        response = {
            "status": "success",
            "message": TranslationManager.get_message(message_key, lang, **kwargs),
            "lang": lang
        }
        
        if data is not None:
            response["data"] = data
        
        return response
    
    @staticmethod
    def error(message_key: str, lang: str = "en", errors: Any = None, **kwargs) -> Dict:
        """
        Generar respuesta de error
        
        Args:
            message_key: Clave del mensaje de error
            lang: Idioma de la respuesta
            errors: Detalles adicionales del error
            **kwargs: Parámetros para el mensaje
        
        Returns:
            Diccionario de respuesta
        """
        response = {
            "status": "error",
            "message": TranslationManager.get_message(message_key, lang, **kwargs),
            "lang": lang
        }
        
        if errors is not None:
            response["errors"] = errors
        
        return response

# =====================================
# Validador con mensajes multiidioma
# =====================================

class Validator:
    """Validador con soporte de i18n"""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: list, lang: str = "en") -> Optional[Dict]:
        """
        Validar campos requeridos
        
        Args:
            data: Datos a validar
            required_fields: Lista de campos requeridos
            lang: Idioma para los mensajes de error
        
        Returns:
            Dict con errores o None si todo es válido
        """
        errors = {}
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                errors[field] = TranslationManager.get_message(
                    "validation.required_field", 
                    lang, 
                    field=field
                )
        
        return errors if errors else None
    
    @staticmethod
    def validate_email(email: str, lang: str = "en") -> Optional[str]:
        """
        Validar formato de email
        
        Args:
            email: Email a validar
            lang: Idioma para el mensaje de error
        
        Returns:
            Mensaje de error o None si es válido
        """
        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        if not re.match(email_pattern, email):
            return TranslationManager.get_message("validation.invalid_email", lang)
        
        return None
    
    @staticmethod
    def validate_password(password: str, lang: str = "en") -> Optional[str]:
        """
        Validar fortaleza de contraseña
        
        Args:
            password: Contraseña a validar
            lang: Idioma para el mensaje de error
        
        Returns:
            Mensaje de error o None si es válida
        """
        if len(password) < 8:
            return TranslationManager.get_message("validation.password_weak", lang)
        
        return None

# =====================================
# Funciones Cloud actualizadas con i18n
# =====================================

@with_i18n
def execute_flow(request, lang="en"):
    """HTTP Cloud Function para ejecutar un flujo con soporte i18n"""
    try:
        request_json = request.get_json()
        
        # Validar campos requeridos
        validation_errors = Validator.validate_required_fields(
            request_json, 
            ['flow_id', 'user_id'], 
            lang
        )
        
        if validation_errors:
            return ApiResponse.error("validation.required_field", lang, errors=validation_errors), 400
        
        flow_id = request_json.get('flow_id')
        user_id = request_json.get('user_id')
        
        # Crear y ejecutar el motor de flujo
        engine = FlowEngine(flow_id, user_id)
        result = asyncio.run(engine.execute_flow())
        
        return ApiResponse.success("flow.execution_completed", result, lang), 200
        
    except ValueError as e:
        if "not found" in str(e):
            return ApiResponse.error("flow.not_found", lang), 404
        return ApiResponse.error("system.error", lang, errors=str(e)), 400
        
    except Exception as e:
        return ApiResponse.error("execution.failed", lang, error=str(e)), 500

@with_i18n
def register_user(request, lang="en"):
    """HTTP Cloud Function para registro de usuario con soporte i18n"""
    try:
        request_json = request.get_json()
        
        # Validar campos requeridos
        validation_errors = Validator.validate_required_fields(
            request_json,
            ['email', 'password', 'name'],
            lang
        )
        
        if validation_errors:
            return ApiResponse.error("validation.required_field", lang, errors=validation_errors), 400
        
        email = request_json.get('email')
        password = request_json.get('password')
        name = request_json.get('name')
        
        # Validar email
        email_error = Validator.validate_email(email, lang)
        if email_error:
            return ApiResponse.error("validation.invalid_email", lang), 400
        
        # Validar contraseña
        password_error = Validator.validate_password(password, lang)
        if password_error:
            return ApiResponse.error("validation.password_weak", lang), 400
        
        # Registrar usuario
        result = asyncio.run(AuthManager.register_user(email, password, name))
        
        return ApiResponse.success("auth.user_created", result, lang), 201
        
    except ValueError as e:
        if "exists" in str(e):
            return ApiResponse.error("auth.user_exists", lang), 400
        return ApiResponse.error("system.error", lang, errors=str(e)), 400
        
    except Exception as e:
        return ApiResponse.error("system.error", lang, errors=str(e)), 500

@with_i18n
def generate_flow_ai(request, lang="en"):
    """HTTP Cloud Function para generar flujo con IA con soporte i18n"""
    try:
        request_json = request.get_json()
        
        # Validar campos requeridos
        validation_errors = Validator.validate_required_fields(
            request_json,
            ['prompt', 'user_id'],
            lang
        )
        
        if validation_errors:
            return ApiResponse.error("validation.required_field", lang, errors=validation_errors), 400
        
        prompt = request_json.get('prompt')
        user_id = request_json.get('user_id')
        
        # Validar longitud del prompt
        if len(prompt) > 1000:
            return ApiResponse.error("ai.prompt_too_long", lang), 400
        
        # Generar flujo con IA
        generator = AIFlowGenerator()
        flow = asyncio.run(generator.generate_flow(prompt, user_id, lang))
        
        return ApiResponse.success("ai.generation_completed", flow, lang), 200
        
    except Exception as e:
        return ApiResponse.error("ai.generation_failed", lang, errors=str(e)), 500

# =====================================
# Notificaciones multiidioma
# =====================================

class NotificationService:
    """Servicio de notificaciones con soporte i18n"""
    
    @staticmethod
    def send_email(to: str, subject_key: str, body_key: str, lang: str = "en", **kwargs):
        """
        Enviar email con contenido traducido
        
        Args:
            to: Dirección de email del destinatario
            subject_key: Clave del asunto
            body_key: Clave del cuerpo del mensaje
            lang: Idioma del mensaje
            **kwargs: Parámetros para el mensaje
        """
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        subject = TranslationManager.get_message(subject_key, lang, **kwargs)
        body = TranslationManager.get_message(body_key, lang, **kwargs)
        
        message = Mail(
            from_email='noreply@agentiqware.com',
            to_emails=to,
            subject=subject,
            html_content=body
        )
        
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_webhook(url: str, event_key: str, data: Dict, lang: str = "en"):
        """
        Enviar webhook con mensaje traducido
        
        Args:
            url: URL del webhook
            event_key: Clave del evento
            data: Datos del evento
            lang: Idioma del mensaje
        """
        import requests
        
        payload = {
            "event": event_key,
            "message": TranslationManager.get_message(event_key, lang),
            "data": data,
            "lang": lang,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False

# =====================================
# Logs multiidioma
# =====================================

class I18nLogger:
    """Logger con soporte de internacionalización"""
    
    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.logger = cloud_logging.Client().logger('agentiqware')
    
    def log_event(self, event_key: str, severity: str = "INFO", **kwargs):
        """
        Registrar evento con mensaje traducido
        
        Args:
            event_key: Clave del evento
            severity: Nivel de severidad
            **kwargs: Parámetros adicionales
        """
        message = TranslationManager.get_message(event_key, self.lang, **kwargs)
        
        log_entry = {
            "message": message,
            "event_key": event_key,
            "lang": self.lang,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self.logger.log_struct(log_entry, severity=severity)
    
    def info(self, event_key: str, **kwargs):
        """Log de información"""
        self.log_event(event_key, "INFO", **kwargs)
    
    def warning(self, event_key: str, **kwargs):
        """Log de advertencia"""
        self.log_event(event_key, "WARNING", **kwargs)
    
    def error(self, event_key: str, **kwargs):
        """Log de error"""
        self.log_event(event_key, "ERROR", **kwargs)
    
    def critical(self, event_key: str, **kwargs):
        """Log crítico"""
        self.log_event(event_key, "CRITICAL", **kwargs)