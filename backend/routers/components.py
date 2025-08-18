"""
Components Router - Handles component-related API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

# Import native Firestore client
try:
    from google.cloud import firestore
    import os
    import subprocess
    
    # Ensure we're using the correct project
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'agentiqware-prod'
    
    # Try to ensure application default credentials are available
    try:
        result = subprocess.run(['gcloud', 'auth', 'application-default', 'print-access-token'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logging.info("Application default credentials are available")
        else:
            logging.warning("Application default credentials may not be available")
    except Exception as e:
        logging.warning(f"Could not check application default credentials: {e}")
    
    # Initialize client as None, will be created when needed
    db = None
    logging.info("Firestore module imported, client will be initialized on demand")
    
except Exception as e:
    logging.error(f"Failed to import Firestore: {e}")
    db = None

logger = logging.getLogger(__name__)

def get_firestore_client():
    """Get Firestore client, initializing if needed"""
    global db
    if db is None:
        try:
            import os
            print(f"[DEBUG] Attempting to initialize Firestore client...")
            print(f"[DEBUG] Current working directory: {os.getcwd()}")
            print(f"[DEBUG] GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'Not set')}")
            logger.info(f"Attempting to initialize Firestore client...")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'Not set')}")
            
            # Simple direct initialization like our test script
            db = firestore.Client(project='agentiqware-prod')
            print(f"[DEBUG] Firestore client created successfully")
            logger.info("Firestore client created successfully")
            
            # Test the connection immediately
            collections = list(db.collections())
            logger.info(f"Connected to Firestore successfully. Found {len(collections)} collections")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Instead of raising, let's log the error and return None for now
            db = None
            raise e
    
    return db

router = APIRouter()

# Component data models
class ComponentMetadata(BaseModel):
    natural_language_description: str
    intent_keywords: List[str]
    use_cases: List[str]
    input_requirements: dict
    output_description: dict
    complexity_level: str
    dependencies: List[str]
    typical_next_steps: List[str]
    error_scenarios: List[str]
    performance_notes: str

class Component(BaseModel):
    id: int
    uid: str
    packageName: str
    actionName: str
    actionDescription: str
    actionGroup: str
    actionLabel: str
    actionIcon: str
    storageEntity: Optional[str] = None
    info: Optional[str] = None
    code: str
    parameters: str
    origin: str
    global_: int = 1  # Using global_ because global is a reserved keyword
    canHaveChildren: Optional[bool] = None
    status: str
    childrenIdent: Optional[str] = None
    blockPropName: Optional[str] = None
    ai_metadata: ComponentMetadata

    class Config:
        # Allow population by field name
        allow_population_by_field_name = True
        # Map global_ to global field
        fields = {'global_': 'global'}

@router.get("/components", response_model=List[Component])
async def get_components():
    """
    Get all components from Firestore (with local file fallback)
    """
    try:
        # First try to load from Firestore
        import os
        print(f"[DEBUG] Attempting Firestore connection...")
        
        # Try to use the same approach as our working test script
        original_cwd = os.getcwd()
        project_root = original_cwd
        if os.path.basename(original_cwd) == 'backend':
            project_root = os.path.dirname(original_cwd)
        
        os.chdir(project_root)
        print(f"[DEBUG] Working from project root: {os.getcwd()}")
        
        direct_db = firestore.Client(project='agentiqware-prod')
        print(f"[DEBUG] Firestore connection successful")
        
        # Restore working directory
        os.chdir(original_cwd)
        
        # Load components from Firestore
        components_ref = direct_db.collection('components')
        docs = components_ref.stream()
        
        components = []
        for doc in docs:
            try:
                component_data = doc.to_dict()
                if component_data and component_data.get('status') == 'S':
                    # Add the document ID as id if not present
                    if 'id' not in component_data:
                        component_data['id'] = doc.id
                    
                    # Ensure required fields have defaults
                    component_data.setdefault('global', 1)
                    component_data.setdefault('status', 'S')
                    component_data.setdefault('origin', 'SmartBots')
                    component_data.setdefault('code', '')
                    component_data.setdefault('parameters', '{}')
                    
                    # Ensure ai_metadata exists
                    if 'ai_metadata' not in component_data:
                        component_data['ai_metadata'] = {
                            'natural_language_description': component_data.get('actionDescription', ''),
                            'intent_keywords': [],
                            'use_cases': [],
                            'input_requirements': {'required_inputs': [], 'optional_inputs': [], 'input_types': {}},
                            'output_description': {'output_type': 'unknown', 'output_description': '', 'output_variable': ''},
                            'complexity_level': 'basic',
                            'dependencies': [],
                            'typical_next_steps': [],
                            'error_scenarios': [],
                            'performance_notes': ''
                        }
                    
                    components.append(component_data)
                    
            except Exception as e:
                print(f"[DEBUG] Error processing component document {doc.id}: {e}")
                continue
        
        print(f"[DEBUG] Retrieved {len(components)} components from Firestore")
        return components
        
    except Exception as firestore_error:
        print(f"[DEBUG] Firestore failed: {firestore_error}, trying local file fallback...")
        
        # Fallback to local file
        try:
            import json
            from pathlib import Path
            
            # Try to find the components file
            components_file = None
            possible_paths = [
                Path("frontend/public/enhanced_components_full.json"),
                Path("../frontend/public/enhanced_components_full.json"),
                Path("enhanced_components_full.json")
            ]
            
            for path in possible_paths:
                if path.exists():
                    components_file = path
                    break
            
            if not components_file:
                raise HTTPException(
                    status_code=503,
                    detail="Neither Firestore nor local file components are available"
                )
            
            print(f"[DEBUG] Loading from local file: {components_file}")
            
            with open(components_file, 'r', encoding='utf-8') as f:
                components_data = json.load(f)
            
            # Filter only active components and format them
            active_components = []
            for comp in components_data:
                if comp.get('status') == 'S':
                    # Ensure required fields and proper types
                    formatted_comp = {
                        'id': comp.get('id', comp.get('actionName', 'unknown')),
                        'uid': str(comp.get('uid', '')),
                        'packageName': str(comp.get('packageName', 'Unknown')),
                        'actionName': str(comp.get('actionName', 'unknown')),
                        'actionDescription': str(comp.get('actionDescription', '')),
                        'actionGroup': str(comp.get('actionGroup', 'Unknown')),
                        'actionLabel': str(comp.get('actionLabel', '')),
                        'actionIcon': str(comp.get('actionIcon', '')),
                        'storageEntity': str(comp.get('storageEntity', '')) if comp.get('storageEntity') is not None else None,
                        'info': str(comp.get('info', '')) if comp.get('info') is not None else None,
                        'code': str(comp.get('code', '')) if comp.get('code') is not None else '',
                        'parameters': str(comp.get('parameters', '{}')) if comp.get('parameters') is not None else '{}',
                        'origin': str(comp.get('origin', 'SmartBots')),
                        'global': int(comp.get('global', 1)),
                        'canHaveChildren': comp.get('canHaveChildren'),
                        'status': str(comp.get('status', 'S')),
                        'childrenIdent': str(comp.get('childrenIdent', '')) if comp.get('childrenIdent') not in [None, True, False] else None,
                        'blockPropName': str(comp.get('blockPropName', '')) if comp.get('blockPropName') is not None else None,
                        'ai_metadata': comp.get('ai_metadata', {
                            'natural_language_description': comp.get('actionDescription', ''),
                            'intent_keywords': [],
                            'use_cases': [],
                            'input_requirements': {'required_inputs': [], 'optional_inputs': [], 'input_types': {}},
                            'output_description': {'output_type': 'unknown', 'output_description': '', 'output_variable': ''},
                            'complexity_level': 'basic',
                            'dependencies': [],
                            'typical_next_steps': [],
                            'error_scenarios': [],
                            'performance_notes': ''
                        })
                    }
                    active_components.append(formatted_comp)
            
            print(f"[DEBUG] Loaded {len(active_components)} components from local file")
            return active_components
            
        except Exception as file_error:
            print(f"[DEBUG] Local file fallback failed: {file_error}")
            raise HTTPException(
                status_code=503,
                detail=f"Both Firestore and local file failed. Firestore: {firestore_error}, File: {file_error}"
            )

@router.get("/components/{component_id}")
async def get_component(component_id: str):
    """
    Get a specific component by ID
    """
    try:
        db = get_firestore_client()
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    
    try:
        doc_ref = db.collection('components').document(component_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Component not found"
            )
        
        component_data = doc.to_dict()
        component_data['id'] = doc.id
        
        return component_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching component {component_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch component: {str(e)}"
        )

@router.get("/components/category/{category}")
async def get_components_by_category(category: str):
    """
    Get components by category (actionGroup)
    """
    try:
        db = get_firestore_client()
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )
    
    try:
        components_ref = db.collection('components')
        query = components_ref.where('actionGroup', '==', category)
        docs = query.stream()
        
        components = []
        for doc in docs:
            component_data = doc.to_dict()
            component_data['id'] = doc.id
            components.append(component_data)
        
        return components
        
    except Exception as e:
        logger.error(f"Error fetching components by category {category}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch components by category: {str(e)}"
        )

@router.get("/health")
async def components_health():
    """
    Health check for components service
    """
    try:
        db = get_firestore_client()
    except Exception as e:
        return {"status": "unhealthy", "firestore": f"error: {str(e)}"}
    
    try:
        # Test Firestore connection
        components_ref = db.collection('components')
        # Try to get one document to test connection
        docs = components_ref.limit(1).stream()
        list(docs)  # Consume the iterator to actually execute the query
        
        return {"status": "healthy", "firestore": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "firestore": f"error: {str(e)}"}