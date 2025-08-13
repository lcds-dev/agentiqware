# =====================================
# Sistema de Facturación y Suscripciones para Agentiqware
# =====================================

import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from google.cloud import firestore
from google.cloud import tasks_v2
import asyncio

# Configuración de Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# =====================================
# Planes de Suscripción
# =====================================

class SubscriptionPlan(Enum):
    """Planes de suscripción disponibles"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class PlanDetails:
    """Detalles de cada plan"""
    name: str
    plan_id: str  # Stripe Price ID
    price_monthly: float
    price_yearly: float
    features: Dict[str, Any]
    limits: Dict[str, int]
    stripe_product_id: str
    stripe_price_monthly_id: str
    stripe_price_yearly_id: str

# Definición de planes
SUBSCRIPTION_PLANS = {
    SubscriptionPlan.FREE: PlanDetails(
        name="Free",
        plan_id="free_plan",
        price_monthly=0,
        price_yearly=0,
        features={
            "flows": 5,
            "executions_per_month": 100,
            "storage_gb": 1,
            "api_calls_per_hour": 100,
            "team_members": 1,
            "version_history_days": 7,
            "support": "community",
            "custom_components": False,
            "webhooks": False,
            "sla": False
        },
        limits={
            "max_flows": 5,
            "max_executions_per_month": 100,
            "max_storage_gb": 1,
            "max_api_calls_per_hour": 100
        },
        stripe_product_id="",
        stripe_price_monthly_id="",
        stripe_price_yearly_id=""
    ),
    
    SubscriptionPlan.STARTER: PlanDetails(
        name="Starter",
        plan_id="starter_plan",
        price_monthly=29,
        price_yearly=290,  # 2 months free
        features={
            "flows": 25,
            "executions_per_month": 1000,
            "storage_gb": 10,
            "api_calls_per_hour": 1000,
            "team_members": 3,
            "version_history_days": 30,
            "support": "email",
            "custom_components": False,
            "webhooks": True,
            "sla": False,
            "scheduling": True,
            "basic_analytics": True
        },
        limits={
            "max_flows": 25,
            "max_executions_per_month": 1000,
            "max_storage_gb": 10,
            "max_api_calls_per_hour": 1000
        },
        stripe_product_id="prod_starter",
        stripe_price_monthly_id="price_starter_monthly",
        stripe_price_yearly_id="price_starter_yearly"
    ),
    
    SubscriptionPlan.PROFESSIONAL: PlanDetails(
        name="Professional",
        plan_id="professional_plan",
        price_monthly=99,
        price_yearly=990,  # 2 months free
        features={
            "flows": 100,
            "executions_per_month": 10000,
            "storage_gb": 50,
            "api_calls_per_hour": 10000,
            "team_members": 10,
            "version_history_days": 90,
            "support": "priority",
            "custom_components": True,
            "webhooks": True,
            "sla": True,
            "sla_uptime": 99.5,
            "scheduling": True,
            "advanced_analytics": True,
            "ai_generation": True,
            "marketplace_access": True,
            "integrations": ["slack", "teams", "salesforce", "google_workspace"]
        },
        limits={
            "max_flows": 100,
            "max_executions_per_month": 10000,
            "max_storage_gb": 50,
            "max_api_calls_per_hour": 10000
        },
        stripe_product_id="prod_professional",
        stripe_price_monthly_id="price_professional_monthly",
        stripe_price_yearly_id="price_professional_yearly"
    ),
    
    SubscriptionPlan.ENTERPRISE: PlanDetails(
        name="Enterprise",
        plan_id="enterprise_plan",
        price_monthly=299,  # Starting price, custom quotes available
        price_yearly=2990,
        features={
            "flows": "unlimited",
            "executions_per_month": "unlimited",
            "storage_gb": 500,
            "api_calls_per_hour": "unlimited",
            "team_members": "unlimited",
            "version_history_days": 365,
            "support": "dedicated",
            "custom_components": True,
            "webhooks": True,
            "sla": True,
            "sla_uptime": 99.9,
            "scheduling": True,
            "advanced_analytics": True,
            "ai_generation": True,
            "marketplace_access": True,
            "white_labeling": True,
            "sso": True,
            "audit_logs": True,
            "custom_integrations": True,
            "on_premise_option": True,
            "integrations": "all"
        },
        limits={
            "max_flows": -1,  # Unlimited
            "max_executions_per_month": -1,
            "max_storage_gb": 500,
            "max_api_calls_per_hour": -1
        },
        stripe_product_id="prod_enterprise",
        stripe_price_monthly_id="price_enterprise_monthly",
        stripe_price_yearly_id="price_enterprise_yearly"
    )
}

# =====================================
# Gestor de Suscripciones
# =====================================

class SubscriptionManager:
    """Gestor principal de suscripciones y facturación"""
    
    def __init__(self):
        self.db = firestore.Client()
        self.stripe = stripe
        
    async def create_customer(
        self,
        user_id: str,
        email: str,
        name: str,
        payment_method_id: Optional[str] = None
    ) -> str:
        """
        Crear un cliente en Stripe
        
        Args:
            user_id: ID del usuario en la base de datos
            email: Email del usuario
            name: Nombre del usuario
            payment_method_id: ID del método de pago (opcional)
        
        Returns:
            ID del cliente en Stripe
        """
        try:
            # Crear cliente en Stripe
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    'user_id': user_id,
                    'platform': 'agentiqware'
                }
            )
            
            # Si se proporciona método de pago, agregarlo
            if payment_method_id:
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=customer.id
                )
                
                # Establecer como método de pago por defecto
                stripe.Customer.modify(
                    customer.id,
                    invoice_settings={
                        'default_payment_method': payment_method_id
                    }
                )
            
            # Guardar en base de datos
            self.db.collection('customers').document(user_id).set({
                'stripe_customer_id': customer.id,
                'email': email,
                'name': name,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            return customer.id
            
        except stripe.error.StripeError as e:
            raise Exception(f"Error creating Stripe customer: {str(e)}")
    
    async def create_subscription(
        self,
        user_id: str,
        plan: SubscriptionPlan,
        billing_cycle: str = "monthly",  # monthly or yearly
        coupon_code: Optional[str] = None,
        trial_days: int = 0
    ) -> Dict[str, Any]:
        """
        Crear una nueva suscripción
        
        Args:
            user_id: ID del usuario
            plan: Plan de suscripción
            billing_cycle: Ciclo de facturación
            coupon_code: Código de cupón (opcional)
            trial_days: Días de prueba (opcional)
        
        Returns:
            Detalles de la suscripción creada
        """
        # Obtener cliente de Stripe
        customer_ref = self.db.collection('customers').document(user_id).get()
        if not customer_ref.exists:
            raise ValueError(f"Customer not found for user {user_id}")
        
        customer_data = customer_ref.to_dict()
        stripe_customer_id = customer_data['stripe_customer_id']
        
        # Obtener detalles del plan
        plan_details = SUBSCRIPTION_PLANS[plan]
        
        # Seleccionar el precio correcto
        if billing_cycle == "yearly":
            price_id = plan_details.stripe_price_yearly_id
        else:
            price_id = plan_details.stripe_price_monthly_id
        
        # Parámetros de suscripción
        subscription_params = {
            'customer': stripe_customer_id,
            'items': [{'price': price_id}],
            'metadata': {
                'user_id': user_id,
                'plan': plan.value,
                'billing_cycle': billing_cycle
            },
            'expand': ['latest_invoice.payment_intent']
        }
        
        # Agregar período de prueba si aplica
        if trial_days > 0:
            subscription_params['trial_period_days'] = trial_days
        
        # Aplicar cupón si existe
        if coupon_code:
            subscription_params['coupon'] = coupon_code
        
        try:
            # Crear suscripción en Stripe
            subscription = stripe.Subscription.create(**subscription_params)
            
            # Guardar en base de datos
            subscription_data = {
                'subscription_id': subscription.id,
                'user_id': user_id,
                'plan': plan.value,
                'billing_cycle': billing_cycle,
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                'trial_end': datetime.fromtimestamp(subscription.trial_end).isoformat() if subscription.trial_end else None,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'features': plan_details.features,
                'limits': plan_details.limits
            }
            
            self.db.collection('subscriptions').document(subscription.id).set(subscription_data)
            
            # Actualizar usuario con el plan
            self.db.collection('users').document(user_id).update({
                'subscription_plan': plan.value,
                'subscription_id': subscription.id,
                'subscription_status': subscription.status,
                'limits': plan_details.limits
            })
            
            # Enviar email de confirmación
            await self._send_subscription_confirmation_email(user_id, plan, billing_cycle)
            
            return subscription_data
            
        except stripe.error.StripeError as e:
            raise Exception(f"Error creating subscription: {str(e)}")
    
    async def update_subscription(
        self,
        subscription_id: str,
        new_plan: SubscriptionPlan,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """
        Actualizar una suscripción existente
        
        Args:
            subscription_id: ID de la suscripción
            new_plan: Nuevo plan
            prorate: Si prorratear el cambio
        
        Returns:
            Suscripción actualizada
        """
        try:
            # Obtener suscripción actual
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Obtener detalles del nuevo plan
            plan_details = SUBSCRIPTION_PLANS[new_plan]
            
            # Determinar el precio basado en el ciclo actual
            current_item = subscription['items']['data'][0]
            billing_cycle = subscription.metadata.get('billing_cycle', 'monthly')
            
            if billing_cycle == "yearly":
                new_price_id = plan_details.stripe_price_yearly_id
            else:
                new_price_id = plan_details.stripe_price_monthly_id
            
            # Actualizar suscripción
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': current_item.id,
                    'price': new_price_id
                }],
                proration_behavior='create_prorations' if prorate else 'none',
                metadata={
                    'plan': new_plan.value,
                    'updated_at': datetime.utcnow().isoformat()
                }
            )
            
            # Actualizar base de datos
            self.db.collection('subscriptions').document(subscription_id).update({
                'plan': new_plan.value,
                'updated_at': datetime.utcnow().isoformat(),
                'features': plan_details.features,
                'limits': plan_details.limits
            })
            
            # Actualizar límites del usuario
            user_id = subscription.metadata['user_id']
            self.db.collection('users').document(user_id).update({
                'subscription_plan': new_plan.value,
                'limits': plan_details.limits
            })
            
            # Registrar el cambio de plan
            await self._log_plan_change(user_id, subscription_id, new_plan)
            
            return {
                'subscription_id': subscription_id,
                'new_plan': new_plan.value,
                'status': 'updated',
                'effective_date': datetime.utcnow().isoformat()
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Error updating subscription: {str(e)}")
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancelar una suscripción
        
        Args:
            subscription_id: ID de la suscripción
            at_period_end: Si cancelar al final del período
            reason: Razón de cancelación
        
        Returns:
            Confirmación de cancelación
        """
        try:
            # Cancelar en Stripe
            if at_period_end:
                # Cancelar al final del período
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                    metadata={
                        'cancellation_reason': reason or 'user_requested',
                        'cancelled_at': datetime.utcnow().isoformat()
                    }
                )
            else:
                # Cancelar inmediatamente
                subscription = stripe.Subscription.delete(subscription_id)
            
            # Actualizar base de datos
            self.db.collection('subscriptions').document(subscription_id).update({
                'status': 'cancelled' if not at_period_end else 'pending_cancellation',
                'cancel_at_period_end': at_period_end,
                'cancellation_reason': reason,
                'cancelled_at': datetime.utcnow().isoformat()
            })
            
            # Obtener usuario
            user_id = subscription.metadata['user_id']
            
            # Si es cancelación inmediata, cambiar a plan gratuito
            if not at_period_end:
                await self._downgrade_to_free(user_id)
            
            # Enviar email de confirmación
            await self._send_cancellation_email(user_id, at_period_end)
            
            # Registrar la cancelación
            await self._log_cancellation(user_id, subscription_id, reason)
            
            return {
                'subscription_id': subscription_id,
                'status': 'cancelled' if not at_period_end else 'pending_cancellation',
                'cancel_at': datetime.fromtimestamp(subscription.cancel_at).isoformat() if at_period_end else datetime.utcnow().isoformat()
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Error cancelling subscription: {str(e)}")
    
    async def add_payment_method(
        self,
        user_id: str,
        payment_method_id: str,
        set_as_default: bool = True
    ) -> Dict[str, Any]:
        """
        Agregar un método de pago
        
        Args:
            user_id: ID del usuario
            payment_method_id: ID del método de pago de Stripe
            set_as_default: Si establecer como predeterminado
        
        Returns:
            Confirmación
        """
        # Obtener cliente
        customer_ref = self.db.collection('customers').document(user_id).get()
        if not customer_ref.exists:
            raise ValueError(f"Customer not found for user {user_id}")
        
        customer_data = customer_ref.to_dict()
        stripe_customer_id = customer_data['stripe_customer_id']
        
        try:
            # Adjuntar método de pago
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer_id
            )
            
            # Establecer como predeterminado si se solicita
            if set_as_default:
                stripe.Customer.modify(
                    stripe_customer_id,
                    invoice_settings={
                        'default_payment_method': payment_method_id
                    }
                )
            
            # Guardar en base de datos
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            
            self.db.collection('payment_methods').document(payment_method_id).set({
                'user_id': user_id,
                'payment_method_id': payment_method_id,
                'type': payment_method.type,
                'card': {
                    'brand': payment_method.card.brand if payment_method.card else None,
                    'last4': payment_method.card.last4 if payment_method.card else None,
                    'exp_month': payment_method.card.exp_month if payment_method.card else None,
                    'exp_year': payment_method.card.exp_year if payment_method.card else None
                } if payment_method.type == 'card' else None,
                'is_default': set_as_default,
                'created_at': datetime.utcnow().isoformat()
            })
            
            return {
                'payment_method_id': payment_method_id,
                'status': 'added',
                'is_default': set_as_default
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Error adding payment method: {str(e)}")
    
    async def get_invoices(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtener facturas del usuario
        
        Args:
            user_id: ID del usuario
            limit: Límite de facturas
        
        Returns:
            Lista de facturas
        """
        # Obtener cliente
        customer_ref = self.db.collection('customers').document(user_id).get()
        if not customer_ref.exists:
            return []
        
        customer_data = customer_ref.to_dict()
        stripe_customer_id = customer_data['stripe_customer_id']
        
        try:
            # Obtener facturas de Stripe
            invoices = stripe.Invoice.list(
                customer=stripe_customer_id,
                limit=limit
            )
            
            # Formatear facturas
            formatted_invoices = []
            for invoice in invoices.data:
                formatted_invoices.append({
                    'invoice_id': invoice.id,
                    'number': invoice.number,
                    'amount': invoice.amount_paid / 100,  # Convertir de centavos
                    'currency': invoice.currency.upper(),
                    'status': invoice.status,
                    'date': datetime.fromtimestamp(invoice.created).isoformat(),
                    'period_start': datetime.fromtimestamp(invoice.period_start).isoformat(),
                    'period_end': datetime.fromtimestamp(invoice.period_end).isoformat(),
                    'pdf_url': invoice.invoice_pdf,
                    'hosted_url': invoice.hosted_invoice_url
                })
            
            return formatted_invoices
            
        except stripe.error.StripeError as e:
            raise Exception(f"Error retrieving invoices: {str(e)}")
    
    async def check_usage_limits(
        self,
        user_id: str,
        resource_type: str,
        amount: int = 1
    ) -> Dict[str, Any]:
        """
        Verificar límites de uso
        
        Args:
            user_id: ID del usuario
            resource_type: Tipo de recurso (flows, executions, storage, api_calls)
            amount: Cantidad a verificar
        
        Returns:
            Estado del límite
        """
        # Obtener usuario y sus límites
        user_ref = self.db.collection('users').document(user_id).get()
        if not user_ref.exists:
            raise ValueError(f"User {user_id} not found")
        
        user_data = user_ref.to_dict()
        limits = user_data.get('limits', {})
        
        # Obtener uso actual
        usage_ref = self.db.collection('usage').document(f"{user_id}_{datetime.utcnow().strftime('%Y-%m')}")
        usage_doc = usage_ref.get()
        
        if usage_doc.exists:
            current_usage = usage_doc.to_dict()
        else:
            current_usage = {
                'flows_created': 0,
                'executions': 0,
                'storage_gb': 0,
                'api_calls': 0
            }
        
        # Mapear tipo de recurso
        resource_map = {
            'flows': ('max_flows', 'flows_created'),
            'executions': ('max_executions_per_month', 'executions'),
            'storage': ('max_storage_gb', 'storage_gb'),
            'api_calls': ('max_api_calls_per_hour', 'api_calls')
        }
        
        if resource_type not in resource_map:
            raise ValueError(f"Invalid resource type: {resource_type}")
        
        limit_key, usage_key = resource_map[resource_type]
        limit = limits.get(limit_key, 0)
        current = current_usage.get(usage_key, 0)
        
        # -1 significa ilimitado
        if limit == -1:
            return {
                'allowed': True,
                'limit': 'unlimited',
                'current': current,
                'remaining': 'unlimited'
            }
        
        # Verificar si se excedería el límite
        would_exceed = (current + amount) > limit
        
        return {
            'allowed': not would_exceed,
            'limit': limit,
            'current': current,
            'remaining': max(0, limit - current),
            'would_exceed': would_exceed,
            'exceeded_by': max(0, (current + amount) - limit) if would_exceed else 0
        }
    
    async def record_usage(
        self,
        user_id: str,
        resource_type: str,
        amount: int = 1
    ) -> None:
        """
        Registrar uso de recursos
        
        Args:
            user_id: ID del usuario
            resource_type: Tipo de recurso
            amount: Cantidad usada
        """
        # Verificar límites primero
        limit_check = await self.check_usage_limits(user_id, resource_type, amount)
        
        if not limit_check['allowed']:
            raise Exception(f"Usage limit exceeded for {resource_type}")
        
        # Registrar uso
        month_key = datetime.utcnow().strftime('%Y-%m')
        usage_ref = self.db.collection('usage').document(f"{user_id}_{month_key}")
        
        # Mapear tipo de recurso
        resource_map = {
            'flows': 'flows_created',
            'executions': 'executions',
            'storage': 'storage_gb',
            'api_calls': 'api_calls'
        }
        
        usage_key = resource_map[resource_type]
        
        # Actualizar o crear registro de uso
        usage_doc = usage_ref.get()
        if usage_doc.exists:
            current_data = usage_doc.to_dict()
            current_data[usage_key] = current_data.get(usage_key, 0) + amount
            current_data['updated_at'] = datetime.utcnow().isoformat()
            usage_ref.update(current_data)
        else:
            usage_data = {
                'user_id': user_id,
                'month': month_key,
                'flows_created': 0,
                'executions': 0,
                'storage_gb': 0,
                'api_calls': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            usage_data[usage_key] = amount
            usage_ref.set(usage_data)
        
        # Si se acerca al límite, enviar notificación
        if limit_check['remaining'] != 'unlimited' and limit_check['remaining'] < limit_check['limit'] * 0.2:
            await self._send_limit_warning_email(user_id, resource_type, limit_check)
    
    # Métodos auxiliares privados
    
    async def _downgrade_to_free(self, user_id: str) -> None:
        """Cambiar usuario a plan gratuito"""
        free_plan = SUBSCRIPTION_PLANS[SubscriptionPlan.FREE]
        
        self.db.collection('users').document(user_id).update({
            'subscription_plan': 'free',
            'subscription_id': None,
            'subscription_status': 'none',
            'limits': free_plan.limits
        })
    
    async def _send_subscription_confirmation_email(
        self,
        user_id: str,
        plan: SubscriptionPlan,
        billing_cycle: str
    ) -> None:
        """Enviar email de confirmación de suscripción"""
        # Implementar envío de email
        pass
    
    async def _send_cancellation_email(
        self,
        user_id: str,
        at_period_end: bool
    ) -> None:
        """Enviar email de confirmación de cancelación"""
        # Implementar envío de email
        pass
    
    async def _send_limit_warning_email(
        self,
        user_id: str,
        resource_type: str,
        limit_info: Dict
    ) -> None:
        """Enviar advertencia de límite próximo"""
        # Implementar envío de email
        pass
    
    async def _log_plan_change(
        self,
        user_id: str,
        subscription_id: str,
        new_plan: SubscriptionPlan
    ) -> None:
        """Registrar cambio de plan"""
        self.db.collection('subscription_events').add({
            'event_type': 'plan_change',
            'user_id': user_id,
            'subscription_id': subscription_id,
            'new_plan': new_plan.value,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def _log_cancellation(
        self,
        user_id: str,
        subscription_id: str,
        reason: Optional[str]
    ) -> None:
        """Registrar cancelación"""
        self.db.collection('subscription_events').add({
            'event_type': 'cancellation',
            'user_id': user_id,
            'subscription_id': subscription_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })

# =====================================
# Webhook Handler para Stripe
# =====================================

def handle_stripe_webhook(request):
    """
    Cloud Function para manejar webhooks de Stripe
    
    Args:
        request: Solicitud HTTP con el webhook
    
    Returns:
        Respuesta HTTP
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verificar firma del webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return {'error': 'Invalid payload'}, 400
    except stripe.error.SignatureVerificationError:
        return {'error': 'Invalid signature'}, 400
    
    # Manejar diferentes tipos de eventos
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Manejar pago exitoso
        handle_successful_payment(payment_intent)
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Manejar pago fallido
        handle_failed_payment(payment_intent)
        
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        # Manejar nueva suscripción
        handle_new_subscription(subscription)
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        # Manejar actualización de suscripción
        handle_subscription_update(subscription)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Manejar cancelación de suscripción
        handle_subscription_cancellation(subscription)
        
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        # Manejar pago de factura exitoso
        handle_invoice_payment(invoice)
        
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        # Manejar fallo en pago de factura
        handle_invoice_payment_failed(invoice)
    
    return {'status': 'success'}, 200

def handle_successful_payment(payment_intent):
    """Manejar pago exitoso"""
    db = firestore.Client()
    
    # Registrar el pago
    db.collection('payments').add({
        'payment_intent_id': payment_intent['id'],
        'amount': payment_intent['amount'] / 100,
        'currency': payment_intent['currency'],
        'status': 'succeeded',
        'customer_id': payment_intent['customer'],
        'metadata': payment_intent['metadata'],
        'created_at': datetime.utcnow().isoformat()
    })

def handle_failed_payment(payment_intent):
    """Manejar pago fallido"""
    db = firestore.Client()
    
    # Registrar el intento fallido
    db.collection('payment_failures').add({
        'payment_intent_id': payment_intent['id'],
        'amount': payment_intent['amount'] / 100,
        'currency': payment_intent['currency'],
        'error': payment_intent.get('last_payment_error', {}),
        'customer_id': payment_intent['customer'],
        'created_at': datetime.utcnow().isoformat()
    })
    
    # Notificar al usuario
    # Implementar notificación

def handle_new_subscription(subscription):
    """Manejar nueva suscripción creada"""
    db = firestore.Client()
    user_id = subscription['metadata'].get('user_id')
    
    if user_id:
        # Actualizar estado del usuario
        db.collection('users').document(user_id).update({
            'subscription_status': subscription['status'],
            'subscription_updated_at': datetime.utcnow().isoformat()
        })

def handle_subscription_update(subscription):
    """Manejar actualización de suscripción"""
    db = firestore.Client()
    
    # Actualizar registro de suscripción
    db.collection('subscriptions').document(subscription['id']).update({
        'status': subscription['status'],
        'current_period_start': datetime.fromtimestamp(subscription['current_period_start']).isoformat(),
        'current_period_end': datetime.fromtimestamp(subscription['current_period_end']).isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    })

def handle_subscription_cancellation(subscription):
    """Manejar cancelación de suscripción"""
    db = firestore.Client()
    user_id = subscription['metadata'].get('user_id')
    
    if user_id:
        # Cambiar a plan gratuito
        free_plan = SUBSCRIPTION_PLANS[SubscriptionPlan.FREE]
        
        db.collection('users').document(user_id).update({
            'subscription_plan': 'free',
            'subscription_id': None,
            'subscription_status': 'cancelled',
            'limits': free_plan.limits,
            'subscription_cancelled_at': datetime.utcnow().isoformat()
        })

def handle_invoice_payment(invoice):
    """Manejar pago de factura exitoso"""
    db = firestore.Client()
    
    # Registrar el pago de factura
    db.collection('invoice_payments').add({
        'invoice_id': invoice['id'],
        'customer_id': invoice['customer'],
        'amount_paid': invoice['amount_paid'] / 100,
        'currency': invoice['currency'],
        'status': 'paid',
        'period_start': datetime.fromtimestamp(invoice['period_start']).isoformat(),
        'period_end': datetime.fromtimestamp(invoice['period_end']).isoformat(),
        'created_at': datetime.utcnow().isoformat()
    })

def handle_invoice_payment_failed(invoice):
    """Manejar fallo en pago de factura"""
    db = firestore.Client()
    
    # Registrar el fallo
    db.collection('invoice_failures').add({
        'invoice_id': invoice['id'],
        'customer_id': invoice['customer'],
        'amount_due': invoice['amount_due'] / 100,
        'currency': invoice['currency'],
        'attempt_count': invoice['attempt_count'],
        'next_payment_attempt': datetime.fromtimestamp(invoice['next_payment_attempt']).isoformat() if invoice.get('next_payment_attempt') else None,
        'created_at': datetime.utcnow().isoformat()
    })
    
    # Notificar al usuario sobre el fallo
    # Implementar notificación

# =====================================
# API Endpoints para Facturación
# =====================================

async def subscribe(request):
    """Endpoint para crear suscripción"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        plan = SubscriptionPlan(data.get('plan'))
        billing_cycle = data.get('billing_cycle', 'monthly')
        
        manager = SubscriptionManager()
        subscription = await manager.create_subscription(
            user_id=user_id,
            plan=plan,
            billing_cycle=billing_cycle
        )
        
        return {'status': 'success', 'data': subscription}, 200
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400

async def upgrade_plan(request):
    """Endpoint para actualizar plan"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        new_plan = SubscriptionPlan(data.get('new_plan'))
        
        manager = SubscriptionManager()
        result = await manager.update_subscription(
            subscription_id=subscription_id,
            new_plan=new_plan
        )
        
        return {'status': 'success', 'data': result}, 200
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400

async def cancel_subscription_endpoint(request):
    """Endpoint para cancelar suscripción"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        at_period_end = data.get('at_period_end', True)
        reason = data.get('reason')
        
        manager = SubscriptionManager()
        result = await manager.cancel_subscription(
            subscription_id=subscription_id,
            at_period_end=at_period_end,
            reason=reason
        )
        
        return {'status': 'success', 'data': result}, 200
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400

async def get_billing_info(request):
    """Endpoint para obtener información de facturación"""
    try:
        user_id = request.args.get('user_id')
        
        manager = SubscriptionManager()
        invoices = await manager.get_invoices(user_id)
        
        # Obtener información de suscripción actual
        user_ref = firestore.Client().collection('users').document(user_id).get()
        user_data = user_ref.to_dict()
        
        return {
            'status': 'success',
            'data': {
                'current_plan': user_data.get('subscription_plan'),
                'subscription_status': user_data.get('subscription_status'),
                'invoices': invoices
            }
        }, 200
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400