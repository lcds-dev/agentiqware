# =====================================
# Sistema de Notificaciones en Tiempo Real para Agentiqware
# =====================================

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

# WebSocket y Comunicación en Tiempo Real
import websockets
from websockets.server import WebSocketServerProtocol
import aioredis
from aioredis.client import PubSub

# Notificaciones Push
from pywebpush import webpush, WebPushException
from fcm_admin import messaging, initialize_app, credentials

# Email
import aiosmtplib
from email.message import EmailMessage
import jinja2

# SMS
from twilio.rest import Client as TwilioClient

# Base de datos y colas
from google.cloud import firestore, pubsub_v1, tasks_v2
import firebase_admin

# Logging
import logging

# =====================================
# Configuración de Notificaciones
# =====================================

@dataclass
class NotificationConfig:
    """Configuración del sistema de notificaciones"""
    
    # WebSocket
    WEBSOCKET_HOST: str = "0.0.0.0"
    WEBSOCKET_PORT: int = 8765
    WEBSOCKET_MAX_CONNECTIONS: int = 10000
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CHANNEL_PREFIX: str = "notifications"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: str = "notifications@agentiqware.com"
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "Agentiqware <notifications@agentiqware.com>"
    
    # SMS (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    
    # Push Notifications
    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_CLAIMS_EMAIL: str = "mailto:push@agentiqware.com"
    
    # Firebase Cloud Messaging
    FCM_CREDENTIALS_PATH: str = "fcm-credentials.json"
    
    # Límites y Throttling
    MAX_NOTIFICATIONS_PER_USER_PER_HOUR: int = 100
    MAX_EMAIL_PER_USER_PER_DAY: int = 50
    MAX_SMS_PER_USER_PER_DAY: int = 20
    MAX_PUSH_PER_USER_PER_HOUR: int = 60
    
    # Retry Policy
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 60
    
    # Batching
    BATCH_SIZE: int = 100
    BATCH_DELAY_SECONDS: float = 0.5

# =====================================
# Tipos de Notificaciones
# =====================================

class NotificationType(Enum):
    """Tipos de notificación"""
    FLOW_STARTED = "flow_started"
    FLOW_COMPLETED = "flow_completed"
    FLOW_FAILED = "flow_failed"
    FLOW_WARNING = "flow_warning"
    
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    SUBSCRIPTION_DOWNGRADED = "subscription_downgraded"
    
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_RETRY = "payment_retry"
    
    USAGE_LIMIT_WARNING = "usage_limit_warning"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    
    SECURITY_ALERT = "security_alert"
    NEW_DEVICE_LOGIN = "new_device_login"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_COMMENT = "collaboration_comment"
    
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_UPDATE = "system_update"
    SYSTEM_DOWNTIME = "system_downtime"
    
    CUSTOM = "custom"

class NotificationPriority(Enum):
    """Prioridad de notificación"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class NotificationChannel(Enum):
    """Canal de notificación"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"

# =====================================
# Modelo de Notificación
# =====================================

@dataclass
class Notification:
    """Modelo de notificación"""
    id: str
    user_id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    channels: List[NotificationChannel]
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    read: bool = False
    delivered: Dict[str, bool] = None
    clicked: bool = False
    action_url: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    actions: Optional[List[Dict[str, str]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'channels': [c.value for c in self.channels],
            'created_at': self.created_at.isoformat(),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'read': self.read,
            'delivered': self.delivered or {},
            'clicked': self.clicked,
            'action_url': self.action_url,
            'icon': self.icon,
            'image': self.image,
            'actions': self.actions
        }

# =====================================
# WebSocket Server
# =====================================

class WebSocketServer:
    """Servidor WebSocket para notificaciones en tiempo real"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.connections: Dict[str, Set[WebSocketServerProtocol]] = {}
        self.redis_client = None
        self.pubsub = None
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Iniciar servidor WebSocket"""
        # Conectar a Redis
        self.redis_client = await aioredis.create_redis_pool(
            f'redis://{self.config.REDIS_HOST}:{self.config.REDIS_PORT}/{self.config.REDIS_DB}'
        )
        
        # Iniciar servidor WebSocket
        async with websockets.serve(
            self.handle_connection,
            self.config.WEBSOCKET_HOST,
            self.config.WEBSOCKET_PORT,
            ping_interval=self.config.WEBSOCKET_PING_INTERVAL,
            ping_timeout=self.config.WEBSOCKET_PING_TIMEOUT
        ):
            self.logger.info(f"WebSocket server started on {self.config.WEBSOCKET_HOST}:{self.config.WEBSOCKET_PORT}")
            
            # Suscribirse a canales de Redis
            await self.subscribe_to_redis()
            
            # Mantener el servidor ejecutándose
            await asyncio.Future()
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Manejar nueva conexión WebSocket"""
        connection_id = str(uuid.uuid4())
        user_id = None
        
        try:
            # Autenticar conexión
            auth_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            auth_data = json.loads(auth_message)
            
            if auth_data.get('type') != 'auth' or not auth_data.get('token'):
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                return
            
            # Verificar token y obtener user_id
            user_id = await self.verify_token(auth_data['token'])
            if not user_id:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid token'
                }))
                return
            
            # Registrar conexión
            if user_id not in self.connections:
                self.connections[user_id] = set()
            self.connections[user_id].add(websocket)
            
            # Confirmar autenticación
            await websocket.send(json.dumps({
                'type': 'auth_success',
                'connection_id': connection_id,
                'user_id': user_id
            }))
            
            self.logger.info(f"WebSocket connection established: {connection_id} for user {user_id}")
            
            # Enviar notificaciones pendientes
            await self.send_pending_notifications(user_id, websocket)
            
            # Mantener conexión abierta
            async for message in websocket:
                await self.handle_message(user_id, message, websocket)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"WebSocket connection closed: {connection_id}")
        except asyncio.TimeoutError:
            self.logger.warning(f"WebSocket connection timeout: {connection_id}")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            # Limpiar conexión
            if user_id and user_id in self.connections:
                self.connections[user_id].discard(websocket)
                if not self.connections[user_id]:
                    del self.connections[user_id]
    
    async def handle_message(self, user_id: str, message: str, websocket: WebSocketServerProtocol):
        """Manejar mensaje del cliente"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Responder a ping
                await websocket.send(json.dumps({'type': 'pong'}))
                
            elif message_type == 'mark_read':
                # Marcar notificación como leída
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(user_id, notification_id)
                    
            elif message_type == 'mark_all_read':
                # Marcar todas las notificaciones como leídas
                await self.mark_all_notifications_read(user_id)
                
            elif message_type == 'subscribe':
                # Suscribirse a un canal específico
                channel = data.get('channel')
                if channel:
                    await self.subscribe_user_to_channel(user_id, channel)
                    
            elif message_type == 'unsubscribe':
                # Desuscribirse de un canal
                channel = data.get('channel')
                if channel:
                    await self.unsubscribe_user_from_channel(user_id, channel)
                    
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def broadcast_to_user(self, user_id: str, notification: Dict[str, Any]):
        """Transmitir notificación a todas las conexiones del usuario"""
        if user_id in self.connections:
            message = json.dumps({
                'type': 'notification',
                'data': notification
            })
            
            # Enviar a todas las conexiones del usuario
            disconnected = set()
            for websocket in self.connections[user_id]:
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
            
            # Limpiar conexiones cerradas
            for websocket in disconnected:
                self.connections[user_id].discard(websocket)
    
    async def subscribe_to_redis(self):
        """Suscribirse a canales de Redis para notificaciones"""
        channel = f"{self.config.REDIS_CHANNEL_PREFIX}:*"
        pubsub = self.redis_client.pubsub()
        await pubsub.psubscribe(channel)
        
        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                await self.handle_redis_message(message)
    
    async def handle_redis_message(self, message: Dict[str, Any]):
        """Manejar mensaje de Redis"""
        try:
            channel = message['channel'].decode()
            data = json.loads(message['data'].decode())
            
            # Extraer user_id del canal
            parts = channel.split(':')
            if len(parts) >= 2:
                user_id = parts[1]
                
                # Transmitir a las conexiones del usuario
                await self.broadcast_to_user(user_id, data)
                
        except Exception as e:
            self.logger.error(f"Error handling Redis message: {e}")
    
    async def verify_token(self, token: str) -> Optional[str]:
        """Verificar token y obtener user_id"""
        # Implementar verificación de JWT
        # Por ahora, retornar un user_id simulado
        return "user_123"
    
    async def send_pending_notifications(self, user_id: str, websocket: WebSocketServerProtocol):
        """Enviar notificaciones pendientes al conectarse"""
        # Obtener notificaciones no leídas de la base de datos
        db = firestore.Client()
        notifications = db.collection('notifications')\
            .where('user_id', '==', user_id)\
            .where('read', '==', False)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(50)\
            .get()
        
        for notification in notifications:
            await websocket.send(json.dumps({
                'type': 'notification',
                'data': notification.to_dict()
            }))
    
    async def mark_notification_read(self, user_id: str, notification_id: str):
        """Marcar notificación como leída"""
        db = firestore.Client()
        db.collection('notifications').document(notification_id).update({
            'read': True,
            'read_at': datetime.utcnow().isoformat()
        })
    
    async def mark_all_notifications_read(self, user_id: str):
        """Marcar todas las notificaciones como leídas"""
        db = firestore.Client()
        batch = db.batch()
        
        notifications = db.collection('notifications')\
            .where('user_id', '==', user_id)\
            .where('read', '==', False)\
            .get()
        
        for notification in notifications:
            batch.update(notification.reference, {
                'read': True,
                'read_at': datetime.utcnow().isoformat()
            })
        
        batch.commit()
    
    async def subscribe_user_to_channel(self, user_id: str, channel: str):
        """Suscribir usuario a un canal"""
        await self.redis_client.sadd(f"channel:{channel}:users", user_id)
    
    async def unsubscribe_user_from_channel(self, user_id: str, channel: str):
        """Desuscribir usuario de un canal"""
        await self.redis_client.srem(f"channel:{channel}:users", user_id)

# =====================================
# Gestor de Notificaciones
# =====================================

class NotificationManager:
    """Gestor principal del sistema de notificaciones"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.db = firestore.Client()
        self.redis_client = None
        self.email_templates = self._load_email_templates()
        self.twilio_client = TwilioClient(
            config.TWILIO_ACCOUNT_SID,
            config.TWILIO_AUTH_TOKEN
        ) if config.TWILIO_ACCOUNT_SID else None
        self.logger = logging.getLogger(__name__)
        
        # Inicializar Firebase Admin para FCM
        if config.FCM_CREDENTIALS_PATH:
            cred = credentials.Certificate(config.FCM_CREDENTIALS_PATH)
            initialize_app(cred)
    
    async def initialize(self):
        """Inicializar gestor de notificaciones"""
        self.redis_client = await aioredis.create_redis_pool(
            f'redis://{self.config.REDIS_HOST}:{self.config.REDIS_PORT}/{self.config.REDIS_DB}'
        )
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None,
        scheduled_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        action_url: Optional[str] = None,
        actions: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Enviar notificación
        
        Args:
            user_id: ID del usuario destinatario
            notification_type: Tipo de notificación
            title: Título de la notificación
            message: Mensaje de la notificación
            data: Datos adicionales
            priority: Prioridad
            channels: Canales de envío
            scheduled_at: Programar para fecha/hora específica
            expires_at: Fecha de expiración
            action_url: URL de acción
            actions: Acciones adicionales
            
        Returns:
            ID de la notificación
        """
        # Verificar límites de rate
        if not await self._check_rate_limits(user_id):
            raise Exception("Rate limit exceeded for user")
        
        # Determinar canales basados en preferencias del usuario
        if not channels:
            channels = await self._get_user_notification_channels(user_id, notification_type)
        
        # Crear notificación
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            channels=channels,
            created_at=datetime.utcnow(),
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            action_url=action_url,
            actions=actions,
            delivered={}
        )
        
        # Guardar en base de datos
        self.db.collection('notifications').document(notification.id).set(
            notification.to_dict()
        )
        
        # Si está programada, crear tarea
        if scheduled_at and scheduled_at > datetime.utcnow():
            await self._schedule_notification(notification)
        else:
            # Enviar inmediatamente
            await self._send_notification_to_channels(notification)
        
        return notification.id
    
    async def _send_notification_to_channels(self, notification: Notification):
        """Enviar notificación a través de los canales especificados"""
        tasks = []
        
        for channel in notification.channels:
            if channel == NotificationChannel.IN_APP:
                tasks.append(self._send_in_app_notification(notification))
            elif channel == NotificationChannel.EMAIL:
                tasks.append(self._send_email_notification(notification))
            elif channel == NotificationChannel.SMS:
                tasks.append(self._send_sms_notification(notification))
            elif channel == NotificationChannel.PUSH:
                tasks.append(self._send_push_notification(notification))
            elif channel == NotificationChannel.WEBSOCKET:
                tasks.append(self._send_websocket_notification(notification))
            elif channel == NotificationChannel.WEBHOOK:
                tasks.append(self._send_webhook_notification(notification))
        
        # Ejecutar todas las tareas en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Actualizar estado de entrega
        delivered = {}
        for i, channel in enumerate(notification.channels):
            if isinstance(results[i], Exception):
                self.logger.error(f"Failed to send {channel.value} notification: {results[i]}")
                delivered[channel.value] = False
            else:
                delivered[channel.value] = True
        
        # Actualizar en base de datos
        self.db.collection('notifications').document(notification.id).update({
            'delivered': delivered
        })
    
    async def _send_in_app_notification(self, notification: Notification):
        """Enviar notificación in-app"""
        # La notificación ya está guardada en la base de datos
        # Solo necesitamos notificar vía WebSocket si el usuario está conectado
        await self._send_websocket_notification(notification)
    
    async def _send_email_notification(self, notification: Notification):
        """Enviar notificación por email"""
        # Obtener email del usuario
        user_doc = self.db.collection('users').document(notification.user_id).get()
        if not user_doc.exists:
            raise ValueError(f"User {notification.user_id} not found")
        
        user_data = user_doc.to_dict()
        email = user_data.get('email')
        
        if not email:
            raise ValueError(f"User {notification.user_id} has no email")
        
        # Crear mensaje
        msg = EmailMessage()
        msg['Subject'] = notification.title
        msg['From'] = self.config.EMAIL_FROM
        msg['To'] = email
        
        # Renderizar plantilla HTML
        html_content = self._render_email_template(
            notification.type,
            {
                'title': notification.title,
                'message': notification.message,
                'action_url': notification.action_url,
                'data': notification.data
            }
        )
        
        msg.set_content(notification.message)
        msg.add_alternative(html_content, subtype='html')
        
        # Enviar email
        async with aiosmtplib.SMTP(
            hostname=self.config.SMTP_HOST,
            port=self.config.SMTP_PORT,
            use_tls=self.config.SMTP_USE_TLS
        ) as smtp:
            await smtp.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            await smtp.send_message(msg)
        
        self.logger.info(f"Email sent to {email} for notification {notification.id}")
    
    async def _send_sms_notification(self, notification: Notification):
        """Enviar notificación por SMS"""
        if not self.twilio_client:
            raise ValueError("SMS not configured")
        
        # Obtener teléfono del usuario
        user_doc = self.db.collection('users').document(notification.user_id).get()
        if not user_doc.exists:
            raise ValueError(f"User {notification.user_id} not found")
        
        user_data = user_doc.to_dict()
        phone = user_data.get('phone')
        
        if not phone:
            raise ValueError(f"User {notification.user_id} has no phone")
        
        # Enviar SMS
        message = self.twilio_client.messages.create(
            body=f"{notification.title}\n{notification.message}",
            from_=self.config.TWILIO_FROM_NUMBER,
            to=phone
        )
        
        self.logger.info(f"SMS sent to {phone} for notification {notification.id}: {message.sid}")
    
    async def _send_push_notification(self, notification: Notification):
        """Enviar notificación push"""
        # Obtener suscripciones push del usuario
        subscriptions = self.db.collection('push_subscriptions')\
            .where('user_id', '==', notification.user_id)\
            .get()
        
        for subscription_doc in subscriptions:
            subscription = subscription_doc.to_dict()
            
            # Web Push
            if subscription.get('type') == 'web':
                await self._send_web_push(subscription, notification)
            
            # Mobile Push (FCM)
            elif subscription.get('type') == 'mobile':
                await self._send_fcm_push(subscription, notification)
    
    async def _send_web_push(self, subscription: Dict[str, Any], notification: Notification):
        """Enviar Web Push notification"""
        try:
            webpush(
                subscription_info=subscription['subscription'],
                data=json.dumps({
                    'title': notification.title,
                    'body': notification.message,
                    'icon': notification.icon or '/icon-192.png',
                    'badge': '/badge.png',
                    'url': notification.action_url,
                    'data': notification.data
                }),
                vapid_private_key=self.config.VAPID_PRIVATE_KEY,
                vapid_claims={
                    'sub': self.config.VAPID_CLAIMS_EMAIL
                }
            )
        except WebPushException as e:
            self.logger.error(f"Web push failed: {e}")
            # Si la suscripción es inválida, eliminarla
            if e.response and e.response.status_code == 410:
                self.db.collection('push_subscriptions').document(subscription['id']).delete()
    
    async def _send_fcm_push(self, subscription: Dict[str, Any], notification: Notification):
        """Enviar Firebase Cloud Messaging push"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.message,
                image=notification.image
            ),
            data=notification.data,
            token=subscription['token'],
            android=messaging.AndroidConfig(
                priority='high' if notification.priority.value >= 3 else 'normal',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#6366f1',
                    sound='default'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=notification.title,
                            body=notification.message
                        ),
                        badge=1,
                        sound='default'
                    )
                )
            )
        )
        
        try:
            response = messaging.send(message)
            self.logger.info(f"FCM message sent: {response}")
        except Exception as e:
            self.logger.error(f"FCM send failed: {e}")
    
    async def _send_websocket_notification(self, notification: Notification):
        """Enviar notificación por WebSocket"""
        # Publicar en Redis para que el servidor WebSocket la transmita
        channel = f"{self.config.REDIS_CHANNEL_PREFIX}:{notification.user_id}"
        await self.redis_client.publish(
            channel,
            json.dumps(notification.to_dict())
        )
    
    async def _send_webhook_notification(self, notification: Notification):
        """Enviar notificación por webhook"""
        # Obtener webhooks del usuario
        webhooks = self.db.collection('webhooks')\
            .where('user_id', '==', notification.user_id)\
            .where('active', '==', True)\
            .get()
        
        import aiohttp
        
        for webhook_doc in webhooks:
            webhook = webhook_doc.to_dict()
            
            # Filtrar por tipo de notificación si está configurado
            if webhook.get('notification_types'):
                if notification.type.value not in webhook['notification_types']:
                    continue
            
            # Enviar webhook
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        webhook['url'],
                        json=notification.to_dict(),
                        headers={
                            'X-Agentiqware-Event': notification.type.value,
                            'X-Agentiqware-Signature': self._generate_webhook_signature(
                                webhook.get('secret'),
                                notification.to_dict()
                            )
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status >= 400:
                            self.logger.error(f"Webhook failed: {response.status}")
                except Exception as e:
                    self.logger.error(f"Webhook error: {e}")
    
    def _generate_webhook_signature(self, secret: str, data: Dict[str, Any]) -> str:
        """Generar firma para webhook"""
        if not secret:
            return ""
        
        import hmac
        import hashlib
        
        payload = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    async def _schedule_notification(self, notification: Notification):
        """Programar notificación para envío futuro"""
        # Usar Cloud Tasks para programar
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(
            project=os.environ.get('GCP_PROJECT_ID'),
            location='us-central1',
            queue='notifications'
        )
        
        # Crear tarea
        task = {
            'http_request': {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': f"https://api.agentiqware.com/v1/notifications/{notification.id}/send",
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'notification_id': notification.id
                }).encode()
            },
            'schedule_time': notification.scheduled_at
        }
        
        response = client.create_task(request={'parent': parent, 'task': task})
        self.logger.info(f"Scheduled notification {notification.id}: {response.name}")
    
    async def _check_rate_limits(self, user_id: str) -> bool:
        """Verificar límites de rate para usuario"""
        key = f"notification_rate:{user_id}:{datetime.utcnow().hour}"
        count = await self.redis_client.incr(key)
        
        if count == 1:
            # Primera notificación en esta hora, establecer expiración
            await self.redis_client.expire(key, 3600)
        
        return count <= self.config.MAX_NOTIFICATIONS_PER_USER_PER_HOUR
    
    async def _get_user_notification_channels(
        self,
        user_id: str,
        notification_type: NotificationType
    ) -> List[NotificationChannel]:
        """Obtener canales de notificación preferidos del usuario"""
        # Obtener preferencias del usuario
        prefs_doc = self.db.collection('notification_preferences').document(user_id).get()
        
        if prefs_doc.exists:
            prefs = prefs_doc.to_dict()
            
            # Verificar si el tipo está deshabilitado
            if notification_type.value in prefs.get('disabled_types', []):
                return []
            
            # Obtener canales para este tipo
            type_channels = prefs.get('type_channels', {}).get(notification_type.value)
            if type_channels:
                return [NotificationChannel(c) for c in type_channels]
            
            # Usar canales por defecto del usuario
            default_channels = prefs.get('default_channels', ['in_app'])
            return [NotificationChannel(c) for c in default_channels]
        
        # Canales por defecto del sistema
        return [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
    
    def _load_email_templates(self) -> jinja2.Environment:
        """Cargar plantillas de email"""
        loader = jinja2.FileSystemLoader('templates/emails')
        return jinja2.Environment(loader=loader, autoescape=True)
    
    def _render_email_template(
        self,
        notification_type: NotificationType,
        context: Dict[str, Any]
    ) -> str:
        """Renderizar plantilla de email"""
        template_name = f"{notification_type.value}.html"
        
        # Si no existe plantilla específica, usar genérica
        try:
            template = self.email_templates.get_template(template_name)
        except jinja2.TemplateNotFound:
            template = self.email_templates.get_template('default.html')
        
        return template.render(**context)

# =====================================
# Servicio de Notificaciones Batch
# =====================================

class BatchNotificationService:
    """Servicio para enviar notificaciones en lote"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.notification_manager = NotificationManager(config)
        self.batch_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Iniciar servicio de procesamiento batch"""
        await self.notification_manager.initialize()
        
        # Iniciar workers
        workers = [
            asyncio.create_task(self.batch_worker())
            for _ in range(4)  # 4 workers paralelos
        ]
        
        await asyncio.gather(*workers)
    
    async def batch_worker(self):
        """Worker para procesar notificaciones en lote"""
        batch = []
        last_process_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Esperar por notificaciones
                timeout = self.config.BATCH_DELAY_SECONDS
                notification = await asyncio.wait_for(
                    self.batch_queue.get(),
                    timeout=timeout
                )
                batch.append(notification)
                
                # Procesar batch si está lleno o ha pasado suficiente tiempo
                current_time = asyncio.get_event_loop().time()
                if (len(batch) >= self.config.BATCH_SIZE or 
                    current_time - last_process_time >= self.config.BATCH_DELAY_SECONDS):
                    
                    await self.process_batch(batch)
                    batch = []
                    last_process_time = current_time
                    
            except asyncio.TimeoutError:
                # Procesar batch pendiente si hay algo
                if batch:
                    await self.process_batch(batch)
                    batch = []
                    last_process_time = asyncio.get_event_loop().time()
            
            except Exception as e:
                self.logger.error(f"Batch worker error: {e}")
    
    async def process_batch(self, notifications: List[Notification]):
        """Procesar lote de notificaciones"""
        self.logger.info(f"Processing batch of {len(notifications)} notifications")
        
        # Agrupar por canal para optimización
        by_channel = {}
        for notification in notifications:
            for channel in notification.channels:
                if channel not in by_channel:
                    by_channel[channel] = []
                by_channel[channel].append(notification)
        
        # Procesar cada canal
        tasks = []
        for channel, channel_notifications in by_channel.items():
            if channel == NotificationChannel.EMAIL:
                tasks.append(self.send_batch_emails(channel_notifications))
            elif channel == NotificationChannel.SMS:
                tasks.append(self.send_batch_sms(channel_notifications))
            elif channel == NotificationChannel.PUSH:
                tasks.append(self.send_batch_push(channel_notifications))
            else:
                # Para otros canales, procesar individualmente
                for notification in channel_notifications:
                    tasks.append(
                        self.notification_manager._send_notification_to_channels(notification)
                    )
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_batch_emails(self, notifications: List[Notification]):
        """Enviar emails en lote"""
        # Optimización: usar una sola conexión SMTP para múltiples emails
        async with aiosmtplib.SMTP(
            hostname=self.config.SMTP_HOST,
            port=self.config.SMTP_PORT,
            use_tls=self.config.SMTP_USE_TLS
        ) as smtp:
            await smtp.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            
            for notification in notifications:
                try:
                    await self.notification_manager._send_email_notification(notification)
                except Exception as e:
                    self.logger.error(f"Failed to send email: {e}")
    
    async def send_batch_sms(self, notifications: List[Notification]):
        """Enviar SMS en lote"""
        # Twilio soporta envío en lote
        for notification in notifications:
            try:
                await self.notification_manager._send_sms_notification(notification)
            except Exception as e:
                self.logger.error(f"Failed to send SMS: {e}")
    
    async def send_batch_push(self, notifications: List[Notification]):
        """Enviar push notifications en lote"""
        # FCM soporta multicast
        messages = []
        
        for notification in notifications:
            # Preparar mensajes
            subscriptions = self.notification_manager.db.collection('push_subscriptions')\
                .where('user_id', '==', notification.user_id)\
                .get()
            
            for subscription_doc in subscriptions:
                subscription = subscription_doc.to_dict()
                
                if subscription.get('type') == 'mobile':
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=notification.title,
                            body=notification.message
                        ),
                        token=subscription['token']
                    )
                    messages.append(message)
        
        # Enviar en lote (máximo 500 por lote en FCM)
        for i in range(0, len(messages), 500):
            batch = messages[i:i+500]
            try:
                response = messaging.send_all(batch)
                self.logger.info(f"Batch FCM send: {response.success_count} success, {response.failure_count} failed")
            except Exception as e:
                self.logger.error(f"Batch FCM failed: {e}")