# =====================================
# Sistema de Plantillas y Marketplace para Agentiqware
# =====================================

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import uuid

# =====================================
# Plantillas Predefinidas del Sistema
# =====================================

class TemplateCategory(Enum):
    """Categorías de plantillas"""
    FINANCE = "finance"
    HR = "human_resources"
    SALES = "sales"
    MARKETING = "marketing"
    IT_OPS = "it_operations"
    DATA_PROCESSING = "data_processing"
    CUSTOMER_SERVICE = "customer_service"
    PRODUCTIVITY = "productivity"

@dataclass
class FlowTemplate:
    """Plantilla de flujo reutilizable"""
    id: str
    name: str
    description: str
    category: TemplateCategory
    tags: List[str]
    author: str
    author_id: str
    version: str
    price: float  # 0 para plantillas gratuitas
    rating: float
    downloads: int
    reviews: int
    is_certified: bool  # Certificado por Agentiqware
    flow_definition: Dict[str, Any]
    requirements: List[str]  # Componentes requeridos
    variables: List[Dict[str, Any]]  # Variables configurables
    preview_image: str
    documentation: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'tags': self.tags,
            'author': self.author,
            'author_id': self.author_id,
            'version': self.version,
            'price': self.price,
            'rating': self.rating,
            'downloads': self.downloads,
            'reviews': self.reviews,
            'is_certified': self.is_certified,
            'flow_definition': self.flow_definition,
            'requirements': self.requirements,
            'variables': self.variables,
            'preview_image': self.preview_image,
            'documentation': self.documentation,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# =====================================
# Plantillas Predefinidas
# =====================================

SYSTEM_TEMPLATES = [
    {
        "id": "tpl_invoice_processing",
        "name": "Invoice Processing Automation",
        "description": "Automatically extract data from invoices, validate, and update accounting systems",
        "category": TemplateCategory.FINANCE,
        "tags": ["invoice", "OCR", "accounting", "automation"],
        "flow_definition": {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "file_monitor",
                    "name": "Monitor Invoice Folder",
                    "position": {"x": 100, "y": 200},
                    "config": {
                        "folder": "${invoice_folder}",
                        "pattern": "*.pdf",
                        "interval": 300
                    }
                },
                {
                    "id": "node_2",
                    "type": "ocr_extract",
                    "name": "Extract Invoice Data",
                    "position": {"x": 300, "y": 200},
                    "config": {
                        "input": "${file_path}",
                        "fields": ["invoice_number", "date", "amount", "vendor"]
                    }
                },
                {
                    "id": "node_3",
                    "type": "data_validation",
                    "name": "Validate Data",
                    "position": {"x": 500, "y": 200},
                    "config": {
                        "rules": [
                            {"field": "amount", "type": "numeric", "min": 0},
                            {"field": "date", "type": "date_format", "format": "YYYY-MM-DD"}
                        ]
                    }
                },
                {
                    "id": "node_4",
                    "type": "condition",
                    "name": "Check Validation",
                    "position": {"x": 700, "y": 200},
                    "config": {
                        "condition": "${validation_result}",
                        "operator": "==",
                        "value": "valid"
                    }
                },
                {
                    "id": "node_5",
                    "type": "database_insert",
                    "name": "Save to Database",
                    "position": {"x": 900, "y": 150},
                    "config": {
                        "connection": "${db_connection}",
                        "table": "invoices",
                        "data": "${invoice_data}"
                    }
                },
                {
                    "id": "node_6",
                    "type": "email_send",
                    "name": "Send Error Alert",
                    "position": {"x": 900, "y": 250},
                    "config": {
                        "to": "${admin_email}",
                        "subject": "Invoice Processing Error",
                        "body": "Failed to process invoice: ${error_details}"
                    }
                }
            ],
            "connections": [
                {"from": "node_1", "to": "node_2"},
                {"from": "node_2", "to": "node_3"},
                {"from": "node_3", "to": "node_4"},
                {"from": "node_4", "to": "node_5", "condition": "true"},
                {"from": "node_4", "to": "node_6", "condition": "false"}
            ]
        },
        "variables": [
            {
                "name": "invoice_folder",
                "type": "string",
                "label": "Invoice Folder Path",
                "required": True,
                "default": "/invoices/incoming"
            },
            {
                "name": "db_connection",
                "type": "connection",
                "label": "Database Connection",
                "required": True
            },
            {
                "name": "admin_email",
                "type": "email",
                "label": "Administrator Email",
                "required": True
            }
        ]
    },
    {
        "id": "tpl_employee_onboarding",
        "name": "Employee Onboarding Workflow",
        "description": "Automate new employee onboarding with account creation, access provisioning, and task assignments",
        "category": TemplateCategory.HR,
        "tags": ["hr", "onboarding", "employee", "automation"],
        "flow_definition": {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "form_trigger",
                    "name": "New Employee Form",
                    "position": {"x": 100, "y": 200},
                    "config": {
                        "form_id": "${onboarding_form}",
                        "trigger": "on_submit"
                    }
                },
                {
                    "id": "node_2",
                    "type": "active_directory",
                    "name": "Create AD Account",
                    "position": {"x": 300, "y": 200},
                    "config": {
                        "action": "create_user",
                        "domain": "${ad_domain}",
                        "user_data": "${employee_data}"
                    }
                },
                {
                    "id": "node_3",
                    "type": "email_create",
                    "name": "Create Email Account",
                    "position": {"x": 500, "y": 200},
                    "config": {
                        "provider": "google_workspace",
                        "email": "${employee_email}",
                        "name": "${employee_name}"
                    }
                },
                {
                    "id": "node_4",
                    "type": "parallel_tasks",
                    "name": "Provision Access",
                    "position": {"x": 700, "y": 200},
                    "config": {
                        "tasks": [
                            {"type": "slack_invite", "channel": "${team_channel}"},
                            {"type": "github_access", "repos": "${github_repos}"},
                            {"type": "vpn_setup", "profile": "${vpn_profile}"}
                        ]
                    }
                },
                {
                    "id": "node_5",
                    "type": "task_create",
                    "name": "Create Onboarding Tasks",
                    "position": {"x": 900, "y": 200},
                    "config": {
                        "system": "asana",
                        "project": "${onboarding_project}",
                        "tasks": "${onboarding_checklist}"
                    }
                }
            ],
            "connections": [
                {"from": "node_1", "to": "node_2"},
                {"from": "node_2", "to": "node_3"},
                {"from": "node_3", "to": "node_4"},
                {"from": "node_4", "to": "node_5"}
            ]
        }
    },
    {
        "id": "tpl_sales_lead_nurture",
        "name": "Sales Lead Nurturing Campaign",
        "description": "Automated lead scoring, segmentation, and personalized email campaigns",
        "category": TemplateCategory.SALES,
        "tags": ["sales", "crm", "email", "marketing", "leads"],
        "flow_definition": {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "crm_trigger",
                    "name": "New Lead Created",
                    "position": {"x": 100, "y": 200},
                    "config": {
                        "crm": "salesforce",
                        "trigger": "lead_created",
                        "filters": {"status": "new"}
                    }
                },
                {
                    "id": "node_2",
                    "type": "lead_scoring",
                    "name": "Calculate Lead Score",
                    "position": {"x": 300, "y": 200},
                    "config": {
                        "scoring_model": "${scoring_model}",
                        "factors": ["company_size", "industry", "engagement"]
                    }
                },
                {
                    "id": "node_3",
                    "type": "condition_branch",
                    "name": "Score Segmentation",
                    "position": {"x": 500, "y": 200},
                    "config": {
                        "branches": [
                            {"condition": "score >= 80", "label": "hot"},
                            {"condition": "score >= 50", "label": "warm"},
                            {"condition": "score < 50", "label": "cold"}
                        ]
                    }
                }
            ]
        }
    },
    {
        "id": "tpl_data_etl_pipeline",
        "name": "Data ETL Pipeline",
        "description": "Extract, transform, and load data from multiple sources to data warehouse",
        "category": TemplateCategory.DATA_PROCESSING,
        "tags": ["etl", "data", "warehouse", "analytics"],
        "flow_definition": {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "schedule_trigger",
                    "name": "Daily Schedule",
                    "position": {"x": 100, "y": 200},
                    "config": {
                        "cron": "0 2 * * *",
                        "timezone": "UTC"
                    }
                },
                {
                    "id": "node_2",
                    "type": "parallel_extract",
                    "name": "Extract from Sources",
                    "position": {"x": 300, "y": 200},
                    "config": {
                        "sources": [
                            {"type": "database", "connection": "${source_db}"},
                            {"type": "api", "endpoint": "${api_endpoint}"},
                            {"type": "csv", "path": "${csv_path}"}
                        ]
                    }
                },
                {
                    "id": "node_3",
                    "type": "data_transform",
                    "name": "Transform Data",
                    "position": {"x": 500, "y": 200},
                    "config": {
                        "transformations": [
                            {"type": "clean_nulls"},
                            {"type": "standardize_dates"},
                            {"type": "aggregate", "group_by": ["category"]}
                        ]
                    }
                },
                {
                    "id": "node_4",
                    "type": "data_validation",
                    "name": "Validate Data Quality",
                    "position": {"x": 700, "y": 200},
                    "config": {
                        "checks": [
                            {"type": "completeness", "threshold": 0.95},
                            {"type": "uniqueness", "columns": ["id"]},
                            {"type": "consistency", "rules": "${validation_rules}"}
                        ]
                    }
                },
                {
                    "id": "node_5",
                    "type": "warehouse_load",
                    "name": "Load to Warehouse",
                    "position": {"x": 900, "y": 200},
                    "config": {
                        "warehouse": "snowflake",
                        "schema": "${target_schema}",
                        "table": "${target_table}",
                        "mode": "append"
                    }
                }
            ]
        }
    },
    {
        "id": "tpl_social_media_monitor",
        "name": "Social Media Monitoring & Response",
        "description": "Monitor social media mentions, analyze sentiment, and auto-respond",
        "category": TemplateCategory.MARKETING,
        "tags": ["social", "monitoring", "sentiment", "marketing"],
        "flow_definition": {
            "nodes": [
                {
                    "id": "node_1",
                    "type": "social_monitor",
                    "name": "Monitor Social Channels",
                    "position": {"x": 100, "y": 200},
                    "config": {
                        "platforms": ["twitter", "facebook", "instagram"],
                        "keywords": "${brand_keywords}",
                        "interval": 60
                    }
                },
                {
                    "id": "node_2",
                    "type": "sentiment_analysis",
                    "name": "Analyze Sentiment",
                    "position": {"x": 300, "y": 200},
                    "config": {
                        "model": "advanced",
                        "languages": ["en", "es"]
                    }
                }
            ]
        }
    }
]

# =====================================
# Gestor del Marketplace
# =====================================

class MarketplaceManager:
    """Gestor del marketplace de plantillas"""
    
    def __init__(self, db_client):
        self.db = db_client
        self.templates_collection = 'marketplace_templates'
        self.purchases_collection = 'template_purchases'
        self.reviews_collection = 'template_reviews'
    
    async def publish_template(
        self,
        flow_id: str,
        user_id: str,
        metadata: Dict[str, Any]
    ) -> FlowTemplate:
        """
        Publicar un flujo como plantilla en el marketplace
        
        Args:
            flow_id: ID del flujo a publicar
            user_id: ID del usuario autor
            metadata: Metadatos de la plantilla
        
        Returns:
            Plantilla publicada
        """
        # Cargar el flujo original
        flow_ref = self.db.collection('flows').document(flow_id)
        flow_doc = flow_ref.get()
        
        if not flow_doc.exists:
            raise ValueError(f"Flow {flow_id} not found")
        
        flow_data = flow_doc.to_dict()
        
        # Limpiar datos sensibles del flujo
        cleaned_flow = self._clean_sensitive_data(flow_data)
        
        # Crear la plantilla
        template = FlowTemplate(
            id=f"tpl_{uuid.uuid4().hex[:12]}",
            name=metadata.get('name'),
            description=metadata.get('description'),
            category=TemplateCategory(metadata.get('category', 'productivity')),
            tags=metadata.get('tags', []),
            author=metadata.get('author_name'),
            author_id=user_id,
            version="1.0.0",
            price=metadata.get('price', 0.0),
            rating=0.0,
            downloads=0,
            reviews=0,
            is_certified=False,
            flow_definition=cleaned_flow,
            requirements=self._extract_requirements(cleaned_flow),
            variables=self._extract_variables(cleaned_flow),
            preview_image=metadata.get('preview_image', ''),
            documentation=metadata.get('documentation', ''),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Guardar en la base de datos
        self.db.collection(self.templates_collection).document(template.id).set(
            template.to_dict()
        )
        
        # Notificar a los suscriptores
        await self._notify_new_template(template)
        
        return template
    
    async def search_templates(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        price_range: Optional[tuple] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "downloads",
        limit: int = 20,
        offset: int = 0
    ) -> List[FlowTemplate]:
        """
        Buscar plantillas en el marketplace
        
        Args:
            query: Texto de búsqueda
            category: Filtro por categoría
            tags: Filtro por tags
            price_range: Rango de precio (min, max)
            min_rating: Rating mínimo
            sort_by: Campo de ordenamiento
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de plantillas que coinciden
        """
        templates_ref = self.db.collection(self.templates_collection)
        
        # Aplicar filtros
        if category:
            templates_ref = templates_ref.where('category', '==', category)
        
        if min_rating:
            templates_ref = templates_ref.where('rating', '>=', min_rating)
        
        if price_range:
            min_price, max_price = price_range
            templates_ref = templates_ref.where('price', '>=', min_price)
            templates_ref = templates_ref.where('price', '<=', max_price)
        
        # Ordenar
        templates_ref = templates_ref.order_by(sort_by, direction='DESCENDING')
        
        # Paginar
        templates_ref = templates_ref.limit(limit).offset(offset)
        
        # Ejecutar consulta
        templates = []
        for doc in templates_ref.stream():
            template_data = doc.to_dict()
            
            # Filtrar por tags si se especificaron
            if tags and not any(tag in template_data.get('tags', []) for tag in tags):
                continue
            
            # Filtrar por query si se especificó
            if query:
                search_text = f"{template_data['name']} {template_data['description']} {' '.join(template_data.get('tags', []))}"
                if query.lower() not in search_text.lower():
                    continue
            
            templates.append(template_data)
        
        return templates
    
    async def install_template(
        self,
        template_id: str,
        user_id: str,
        workspace_id: str,
        configuration: Dict[str, Any]
    ) -> str:
        """
        Instalar una plantilla en el workspace del usuario
        
        Args:
            template_id: ID de la plantilla
            user_id: ID del usuario
            workspace_id: ID del workspace
            configuration: Configuración de variables
        
        Returns:
            ID del flujo creado
        """
        # Cargar la plantilla
        template_ref = self.db.collection(self.templates_collection).document(template_id)
        template_doc = template_ref.get()
        
        if not template_doc.exists:
            raise ValueError(f"Template {template_id} not found")
        
        template_data = template_doc.to_dict()
        
        # Verificar compra si es de pago
        if template_data['price'] > 0:
            if not await self._verify_purchase(user_id, template_id):
                raise ValueError("Template not purchased")
        
        # Crear una copia del flujo
        flow_definition = template_data['flow_definition'].copy()
        
        # Aplicar configuración de variables
        flow_definition = self._apply_configuration(flow_definition, configuration)
        
        # Crear el nuevo flujo
        new_flow_id = f"flow_{uuid.uuid4().hex[:12]}"
        flow_data = {
            'id': new_flow_id,
            'name': f"{template_data['name']} (from template)",
            'user_id': user_id,
            'workspace_id': workspace_id,
            'template_id': template_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            **flow_definition
        }
        
        # Guardar el flujo
        self.db.collection('flows').document(new_flow_id).set(flow_data)
        
        # Incrementar contador de descargas
        template_ref.update({
            'downloads': template_data['downloads'] + 1
        })
        
        # Registrar la instalación
        await self._record_installation(template_id, user_id, new_flow_id)
        
        return new_flow_id
    
    async def review_template(
        self,
        template_id: str,
        user_id: str,
        rating: int,
        comment: str
    ) -> None:
        """
        Agregar una reseña a una plantilla
        
        Args:
            template_id: ID de la plantilla
            user_id: ID del usuario
            rating: Calificación (1-5)
            comment: Comentario de la reseña
        """
        # Verificar que el usuario haya instalado la plantilla
        if not await self._verify_installation(user_id, template_id):
            raise ValueError("User has not installed this template")
        
        # Crear la reseña
        review = {
            'id': f"review_{uuid.uuid4().hex[:12]}",
            'template_id': template_id,
            'user_id': user_id,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.utcnow().isoformat(),
            'helpful_count': 0
        }
        
        # Guardar la reseña
        self.db.collection(self.reviews_collection).document(review['id']).set(review)
        
        # Actualizar el rating promedio de la plantilla
        await self._update_template_rating(template_id)
    
    async def get_template_analytics(
        self,
        template_id: str,
        author_id: str
    ) -> Dict[str, Any]:
        """
        Obtener analíticas de una plantilla
        
        Args:
            template_id: ID de la plantilla
            author_id: ID del autor (para verificación)
        
        Returns:
            Diccionario con analíticas
        """
        # Verificar que el usuario sea el autor
        template_ref = self.db.collection(self.templates_collection).document(template_id)
        template_doc = template_ref.get()
        
        if not template_doc.exists:
            raise ValueError(f"Template {template_id} not found")
        
        template_data = template_doc.to_dict()
        
        if template_data['author_id'] != author_id:
            raise ValueError("Unauthorized: User is not the template author")
        
        # Recopilar analíticas
        analytics = {
            'downloads': template_data['downloads'],
            'rating': template_data['rating'],
            'reviews': template_data['reviews'],
            'revenue': await self._calculate_revenue(template_id),
            'installations_by_date': await self._get_installations_timeline(template_id),
            'user_demographics': await self._get_user_demographics(template_id),
            'performance_metrics': await self._get_performance_metrics(template_id)
        }
        
        return analytics
    
    # Métodos auxiliares privados
    
    def _clean_sensitive_data(self, flow_data: Dict) -> Dict:
        """Limpiar datos sensibles del flujo"""
        cleaned = flow_data.copy()
        
        # Remover credenciales y tokens
        sensitive_keys = ['api_key', 'password', 'token', 'secret', 'credential']
        
        def clean_dict(d):
            for key in list(d.keys()):
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    d[key] = '${' + key + '}'
                elif isinstance(d[key], dict):
                    clean_dict(d[key])
        
        if 'nodes' in cleaned:
            for node in cleaned['nodes']:
                if 'config' in node:
                    clean_dict(node['config'])
        
        return cleaned
    
    def _extract_requirements(self, flow_data: Dict) -> List[str]:
        """Extraer componentes requeridos del flujo"""
        requirements = set()
        
        if 'nodes' in flow_data:
            for node in flow_data['nodes']:
                requirements.add(node.get('type', 'unknown'))
        
        return list(requirements)
    
    def _extract_variables(self, flow_data: Dict) -> List[Dict]:
        """Extraer variables configurables del flujo"""
        variables = []
        variable_pattern = r'\$\{([^}]+)\}'
        
        import re
        
        def extract_from_dict(d, path=''):
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, str):
                    matches = re.findall(variable_pattern, value)
                    for match in matches:
                        if not any(v['name'] == match for v in variables):
                            variables.append({
                                'name': match,
                                'type': 'string',
                                'label': match.replace('_', ' ').title(),
                                'required': True,
                                'path': current_path
                            })
                elif isinstance(value, dict):
                    extract_from_dict(value, current_path)
        
        if 'nodes' in flow_data:
            for node in flow_data['nodes']:
                if 'config' in node:
                    extract_from_dict(node['config'], f"node_{node.get('id', 'unknown')}")
        
        return variables
    
    def _apply_configuration(
        self,
        flow_definition: Dict,
        configuration: Dict[str, Any]
    ) -> Dict:
        """Aplicar configuración de variables al flujo"""
        import re
        
        def replace_variables(obj):
            if isinstance(obj, str):
                for var_name, var_value in configuration.items():
                    obj = obj.replace(f'${{{var_name}}}', str(var_value))
                return obj
            elif isinstance(obj, dict):
                return {k: replace_variables(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_variables(item) for item in obj]
            else:
                return obj
        
        return replace_variables(flow_definition)
    
    async def _verify_purchase(self, user_id: str, template_id: str) -> bool:
        """Verificar si el usuario compró la plantilla"""
        purchase_ref = self.db.collection(self.purchases_collection)
        purchases = purchase_ref.where('user_id', '==', user_id).where('template_id', '==', template_id).get()
        return len(purchases) > 0
    
    async def _verify_installation(self, user_id: str, template_id: str) -> bool:
        """Verificar si el usuario instaló la plantilla"""
        flows_ref = self.db.collection('flows')
        flows = flows_ref.where('user_id', '==', user_id).where('template_id', '==', template_id).get()
        return len(flows) > 0
    
    async def _record_installation(
        self,
        template_id: str,
        user_id: str,
        flow_id: str
    ) -> None:
        """Registrar la instalación de una plantilla"""
        installation = {
            'id': f"inst_{uuid.uuid4().hex[:12]}",
            'template_id': template_id,
            'user_id': user_id,
            'flow_id': flow_id,
            'installed_at': datetime.utcnow().isoformat()
        }
        
        self.db.collection('template_installations').document(installation['id']).set(
            installation
        )
    
    async def _update_template_rating(self, template_id: str) -> None:
        """Actualizar el rating promedio de una plantilla"""
        reviews_ref = self.db.collection(self.reviews_collection)
        reviews = reviews_ref.where('template_id', '==', template_id).stream()
        
        total_rating = 0
        count = 0
        
        for review in reviews:
            review_data = review.to_dict()
            total_rating += review_data['rating']
            count += 1
        
        if count > 0:
            avg_rating = total_rating / count
            
            template_ref = self.db.collection(self.templates_collection).document(template_id)
            template_ref.update({
                'rating': round(avg_rating, 2),
                'reviews': count
            })
    
    async def _notify_new_template(self, template: FlowTemplate) -> None:
        """Notificar a los suscriptores sobre una nueva plantilla"""
        # Implementar lógica de notificación
        pass
    
    async def _calculate_revenue(self, template_id: str) -> float:
        """Calcular ingresos totales de una plantilla"""
        purchases_ref = self.db.collection(self.purchases_collection)
        purchases = purchases_ref.where('template_id', '==', template_id).stream()
        
        total_revenue = 0.0
        for purchase in purchases:
            purchase_data = purchase.to_dict()
            total_revenue += purchase_data.get('amount', 0)
        
        return total_revenue
    
    async def _get_installations_timeline(self, template_id: str) -> List[Dict]:
        """Obtener timeline de instalaciones"""
        # Implementar lógica para obtener instalaciones por fecha
        return []
    
    async def _get_user_demographics(self, template_id: str) -> Dict:
        """Obtener demografía de usuarios"""
        # Implementar lógica para obtener demografía
        return {}
    
    async def _get_performance_metrics(self, template_id: str) -> Dict:
        """Obtener métricas de rendimiento"""
        # Implementar lógica para obtener métricas
        return {}