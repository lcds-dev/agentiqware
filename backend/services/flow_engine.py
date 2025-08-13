# Agentiqware Backend Architecture - Google Cloud Platform
# =========================================================

# requirements.txt
"""
google-cloud-firestore==2.11.1
google-cloud-storage==2.10.0
google-cloud-pubsub==2.18.0
google-cloud-tasks==2.13.1
google-cloud-logging==3.5.0
google-auth==2.20.0
pandas==2.0.3
openpyxl==3.1.2
pyautogui==0.9.54
pynput==1.7.6
anthropic==0.23.1
fastapi==0.100.0
pydantic==2.0.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==4.6.0
"""

# =====================================
# 1. MAIN CLOUD FUNCTION - Flow Executor
# =====================================

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import traceback

from google.cloud import firestore
from google.cloud import storage
from google.cloud import pubsub_v1
from google.cloud import tasks_v2
from google.cloud import logging as cloud_logging

# Initialize clients
db = firestore.Client()
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()
tasks_client = tasks_v2.CloudTasksClient()
logging_client = cloud_logging.Client()

# =====================================
# Component Registry
# =====================================

@dataclass
class ComponentDefinition:
    """Component definition from JSON"""
    id: str
    name: str
    category: str
    config: Dict[str, Any]
    executor_class: str

class ComponentExecutor:
    """Base class for component executors"""
    
    def __init__(self, node_config: Dict[str, Any], context: Dict[str, Any]):
        self.config = node_config
        self.context = context
        self.variables = context.get('variables', {})
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the component logic"""
        raise NotImplementedError
    
    def resolve_variable(self, value: str) -> Any:
        """Resolve variable references like ${variable_name}"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            var_name = value[2:-1]
            return self.variables.get(var_name, value)
        return value

# =====================================
# Component Executors
# =====================================

class FileSearchExecutor(ComponentExecutor):
    """Executor for file search component"""
    
    async def execute(self) -> Dict[str, Any]:
        import glob
        import os
        
        folder = self.resolve_variable(self.config.get('folder', ''))
        pattern = self.resolve_variable(self.config.get('pattern', '*.*'))
        include_subfolders = self.config.get('include_subfolders', 'no') == 'yes'
        
        if include_subfolders:
            search_pattern = os.path.join(folder, '**', pattern)
            files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(folder, pattern)
            files = glob.glob(search_pattern)
        
        # Store result in variable
        result_var = self.config.get('result', 'file_search_result')
        self.variables[result_var] = files
        
        return {
            'status': 'success',
            'files_found': len(files),
            'result_variable': result_var
        }

class DataFrameMergeExecutor(ComponentExecutor):
    """Executor for DataFrame merge component"""
    
    async def execute(self) -> Dict[str, Any]:
        handler = self.resolve_variable(self.config.get('handler', ''))
        dataframes_str = self.resolve_variable(self.config.get('dataframes', ''))
        direction = self.config.get('direction', 'horizontal')
        
        # Parse dataframe references
        df_names = [df.strip() for df in dataframes_str.split(',')]
        dataframes = []
        
        for df_name in df_names:
            if df_name in self.variables:
                dataframes.append(self.variables[df_name])
        
        if not dataframes:
            raise ValueError("No dataframes found to merge")
        
        # Merge dataframes
        if direction == 'horizontal':
            result_df = pd.concat(dataframes, axis=1)
        else:
            result_df = pd.concat(dataframes, axis=0, ignore_index=True)
        
        # Store result
        self.variables[handler] = result_df
        
        return {
            'status': 'success',
            'merged_shape': result_df.shape,
            'result_variable': handler
        }

class ExcelReaderExecutor(ComponentExecutor):
    """Executor for Excel reader component"""
    
    async def execute(self) -> Dict[str, Any]:
        file_name = self.resolve_variable(self.config.get('excel_file_name', ''))
        sheet_name = self.resolve_variable(self.config.get('sheet_name', 'Sheet1'))
        destination = self.config.get('destination', 'excel_data')
        
        # Read Excel file
        if file_name.startswith('gs://'):
            # Read from Google Cloud Storage
            bucket_name = file_name.split('/')[2]
            blob_path = '/'.join(file_name.split('/')[3:])
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            content = blob.download_as_bytes()
            df = pd.read_excel(content, sheet_name=sheet_name)
        else:
            # Read from local file
            df = pd.read_excel(file_name, sheet_name=sheet_name)
        
        # Store in variables
        self.variables[destination] = df
        
        return {
            'status': 'success',
            'rows': len(df),
            'columns': len(df.columns),
            'result_variable': destination
        }

class ConditionalExecutor(ComponentExecutor):
    """Executor for conditional branching"""
    
    async def execute(self) -> Dict[str, Any]:
        left_value = self.resolve_variable(self.config.get('left_value', ''))
        operator = self.config.get('operator', '==')
        right_value = self.resolve_variable(self.config.get('right_value', ''))
        
        # Evaluate condition
        result = False
        if operator == '==':
            result = left_value == right_value
        elif operator == '!=':
            result = left_value != right_value
        elif operator == '>':
            result = float(left_value) > float(right_value)
        elif operator == '<':
            result = float(left_value) < float(right_value)
        elif operator == '>=':
            result = float(left_value) >= float(right_value)
        elif operator == '<=':
            result = float(left_value) <= float(right_value)
        elif operator == 'contains':
            result = str(right_value) in str(left_value)
        
        return {
            'status': 'success',
            'condition_result': result,
            'next_branch': 'true' if result else 'false'
        }

class RPAAutomationExecutor(ComponentExecutor):
    """Base executor for RPA automation components"""
    
    async def execute_mouse_click(self) -> Dict[str, Any]:
        import pyautogui
        
        x = int(self.resolve_variable(self.config.get('x', 0)))
        y = int(self.resolve_variable(self.config.get('y', 0)))
        button = self.config.get('button', 'left')
        clicks = int(self.config.get('clicks', 1))
        
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        
        return {
            'status': 'success',
            'action': 'mouse_click',
            'position': {'x': x, 'y': y}
        }
    
    async def execute_keyboard_input(self) -> Dict[str, Any]:
        import pyautogui
        
        text = self.resolve_variable(self.config.get('text', ''))
        delay = float(self.config.get('delay', 0.1))
        special_keys = self.config.get('special_keys', [])
        
        # Handle special keys
        for key in special_keys:
            pyautogui.press(key)
        
        # Type text
        pyautogui.typewrite(text, interval=delay)
        
        return {
            'status': 'success',
            'action': 'keyboard_input',
            'text_length': len(text)
        }

# =====================================
# Flow Engine
# =====================================

class FlowEngine:
    """Main flow execution engine"""
    
    def __init__(self, flow_id: str, user_id: str):
        self.flow_id = flow_id
        self.user_id = user_id
        self.execution_id = None
        self.context = {
            'variables': {},
            'execution_history': [],
            'current_node': None
        }
        self.executors = {
            'file_search': FileSearchExecutor,
            'dataframe_merge': DataFrameMergeExecutor,
            'excel_reader': ExcelReaderExecutor,
            'condition': ConditionalExecutor,
            'mouse_click': RPAAutomationExecutor,
            'keyboard_input': RPAAutomationExecutor
        }
    
    async def load_flow(self) -> Dict[str, Any]:
        """Load flow definition from Firestore"""
        flow_ref = db.collection('flows').document(self.flow_id)
        flow_doc = flow_ref.get()
        
        if not flow_doc.exists:
            raise ValueError(f"Flow {self.flow_id} not found")
        
        return flow_doc.to_dict()
    
    async def execute_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node"""
        node_type = node.get('type')
        executor_class = self.executors.get(node_type)
        
        if not executor_class:
            raise ValueError(f"Unknown node type: {node_type}")
        
        # Create executor instance
        executor = executor_class(node.get('data', {}), self.context)
        
        # Execute based on node type
        if node_type == 'mouse_click':
            result = await executor.execute_mouse_click()
        elif node_type == 'keyboard_input':
            result = await executor.execute_keyboard_input()
        else:
            result = await executor.execute()
        
        # Log execution
        self.context['execution_history'].append({
            'node_id': node.get('id'),
            'node_type': node_type,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        })
        
        return result
    
    async def execute_flow(self) -> Dict[str, Any]:
        """Execute the complete flow"""
        try:
            # Create execution record
            self.execution_id = f"exec_{self.flow_id}_{datetime.utcnow().timestamp()}"
            
            # Load flow definition
            flow_data = await self.load_flow()
            nodes = flow_data.get('nodes', [])
            connections = flow_data.get('connections', [])
            
            # Build execution graph
            graph = self.build_execution_graph(nodes, connections)
            
            # Start execution from entry point
            entry_node = self.find_entry_node(nodes, connections)
            await self.execute_graph(entry_node, nodes, connections)
            
            # Save execution results
            await self.save_execution_results('completed')
            
            return {
                'status': 'success',
                'execution_id': self.execution_id,
                'nodes_executed': len(self.context['execution_history'])
            }
            
        except Exception as e:
            # Log error
            await self.save_execution_results('failed', str(e))
            raise
    
    def build_execution_graph(self, nodes: List[Dict], connections: List[Dict]) -> Dict:
        """Build node execution graph"""
        graph = {}
        for conn in connections:
            from_node = conn.get('from')
            to_node = conn.get('to')
            output = conn.get('fromOutput', 'default')
            
            if from_node not in graph:
                graph[from_node] = {}
            
            if output not in graph[from_node]:
                graph[from_node][output] = []
            
            graph[from_node][output].append(to_node)
        
        return graph
    
    def find_entry_node(self, nodes: List[Dict], connections: List[Dict]) -> Dict:
        """Find the entry node (node with no incoming connections)"""
        incoming = {conn.get('to') for conn in connections}
        for node in nodes:
            if node.get('id') not in incoming:
                return node
        return nodes[0] if nodes else None
    
    async def execute_graph(self, current_node: Dict, nodes: List[Dict], connections: List[Dict]):
        """Execute nodes following the graph"""
        if not current_node:
            return
        
        # Execute current node
        result = await self.execute_node(current_node)
        
        # Find next nodes
        node_id = current_node.get('id')
        next_connections = [c for c in connections if c.get('from') == node_id]
        
        # Handle conditional branching
        if current_node.get('type') == 'condition':
            branch = result.get('next_branch', 'default')
            next_connections = [c for c in next_connections if c.get('fromOutput') == branch]
        
        # Execute next nodes
        for conn in next_connections:
            next_node_id = conn.get('to')
            next_node = next((n for n in nodes if n.get('id') == next_node_id), None)
            if next_node:
                await self.execute_graph(next_node, nodes, connections)
    
    async def save_execution_results(self, status: str, error: str = None):
        """Save execution results to Firestore"""
        execution_data = {
            'execution_id': self.execution_id,
            'flow_id': self.flow_id,
            'user_id': self.user_id,
            'status': status,
            'start_time': self.context['execution_history'][0]['timestamp'] if self.context['execution_history'] else None,
            'end_time': datetime.utcnow().isoformat(),
            'nodes_executed': len(self.context['execution_history']),
            'execution_history': self.context['execution_history'],
            'variables': self.context['variables'],
            'error': error
        }
        
        db.collection('executions').document(self.execution_id).set(execution_data)

# =====================================
# Main Cloud Function Entry Points
# =====================================

def execute_flow(request):
    """HTTP Cloud Function to execute a flow"""
    try:
        request_json = request.get_json()
        flow_id = request_json.get('flow_id')
        user_id = request_json.get('user_id')
        
        if not flow_id or not user_id:
            return {'error': 'Missing flow_id or user_id'}, 400
        
        # Create and run flow engine
        engine = FlowEngine(flow_id, user_id)
        result = asyncio.run(engine.execute_flow())
        
        return result, 200
        
    except Exception as e:
        return {'error': str(e), 'trace': traceback.format_exc()}, 500

def schedule_flow(request):
    """HTTP Cloud Function to schedule flow execution"""
    try:
        request_json = request.get_json()
        flow_id = request_json.get('flow_id')
        user_id = request_json.get('user_id')
        schedule = request_json.get('schedule')  # cron expression
        
        # Create Cloud Scheduler job
        # Implementation would use Cloud Scheduler API
        
        return {'status': 'scheduled', 'flow_id': flow_id}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

# =====================================
# AI Flow Generator
# =====================================

class AIFlowGenerator:
    """Generate flows from natural language using AI"""
    
    def __init__(self):
        self.components = self.load_component_definitions()
    
    def load_component_definitions(self) -> List[ComponentDefinition]:
        """Load all available component definitions"""
        components_ref = db.collection('components')
        components = []
        
        for doc in components_ref.stream():
            comp_data = doc.to_dict()
            components.append(ComponentDefinition(**comp_data))
        
        return components
    
    async def generate_flow(self, prompt: str, user_id: str) -> Dict[str, Any]:
        """Generate flow from natural language prompt"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        # Prepare component descriptions for AI
        component_descriptions = [
            f"- {comp.name} ({comp.id}): {comp.category} - Fields: {comp.config.get('fields', [])}"
            for comp in self.components
        ]
        
        # Create AI prompt
        ai_prompt = f"""
        You are an RPA flow designer. Create a flow JSON structure based on this request:
        "{prompt}"
        
        Available components:
        {chr(10).join(component_descriptions)}
        
        Return a valid JSON with:
        - nodes: array of node objects with id, type, name, position, and data
        - connections: array of connection objects with from, to, fromOutput, toInput
        
        Make the flow logical and efficient.
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": ai_prompt}]
        )
        
        # Parse AI response
        flow_json = json.loads(response.content[0].text)
        
        # Save generated flow
        flow_id = f"flow_{datetime.utcnow().timestamp()}"
        flow_data = {
            'id': flow_id,
            'name': f"AI Generated: {prompt[:50]}",
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'ai_generated': True,
            'prompt': prompt,
            **flow_json
        }
        
        db.collection('flows').document(flow_id).set(flow_data)
        
        return flow_data

def generate_flow_ai(request):
    """HTTP Cloud Function to generate flow with AI"""
    try:
        request_json = request.get_json()
        prompt = request_json.get('prompt')
        user_id = request_json.get('user_id')
        
        generator = AIFlowGenerator()
        flow = asyncio.run(generator.generate_flow(prompt, user_id))
        
        return flow, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

# =====================================
# Version Control System
# =====================================

class FlowVersionControl:
    """Manage flow versions and history"""
    
    @staticmethod
    async def save_version(flow_id: str, flow_data: Dict[str, Any], user_id: str, message: str = None):
        """Save a new version of a flow"""
        version_id = f"v_{datetime.utcnow().timestamp()}"
        
        version_data = {
            'version_id': version_id,
            'flow_id': flow_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'message': message or 'Auto-saved',
            'flow_data': flow_data
        }
        
        # Save to versions collection
        db.collection('flow_versions').document(f"{flow_id}_{version_id}").set(version_data)
        
        return version_id
    
    @staticmethod
    async def get_versions(flow_id: str) -> List[Dict]:
        """Get all versions of a flow"""
        versions_ref = db.collection('flow_versions')
        query = versions_ref.where('flow_id', '==', flow_id).order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        versions = []
        for doc in query.stream():
            versions.append(doc.to_dict())
        
        return versions
    
    @staticmethod
    async def restore_version(flow_id: str, version_id: str) -> Dict[str, Any]:
        """Restore a specific version of a flow"""
        version_ref = db.collection('flow_versions').document(f"{flow_id}_{version_id}")
        version_doc = version_ref.get()
        
        if not version_doc.exists:
            raise ValueError(f"Version {version_id} not found")
        
        version_data = version_doc.to_dict()
        flow_data = version_data.get('flow_data')
        
        # Update current flow
        db.collection('flows').document(flow_id).set(flow_data)
        
        # Create restore record
        await FlowVersionControl.save_version(
            flow_id, 
            flow_data, 
            version_data.get('user_id'),
            f"Restored from version {version_id}"
        )
        
        return flow_data

# =====================================
# Authentication & User Management
# =====================================

from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"

class AuthManager:
    """Handle user authentication and authorization"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def register_user(email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user"""
        # Check if user exists
        users_ref = db.collection('users')
        existing = users_ref.where('email', '==', email).get()
        
        if existing:
            raise ValueError("User already exists")
        
        # Create user
        user_id = f"user_{datetime.utcnow().timestamp()}"
        user_data = {
            'user_id': user_id,
            'email': email,
            'name': name,
            'password_hash': AuthManager.hash_password(password),
            'created_at': datetime.utcnow().isoformat(),
            'subscription': 'free',
            'limits': {
                'flows': 5,
                'executions_per_day': 100,
                'storage_gb': 1
            }
        }
        
        db.collection('users').document(user_id).set(user_data)
        
        # Create access token
        access_token = AuthManager.create_access_token(
            data={"sub": user_id, "email": email}
        )
        
        return {
            'user_id': user_id,
            'email': email,
            'access_token': access_token
        }

def register_user(request):
    """HTTP Cloud Function for user registration"""
    try:
        request_json = request.get_json()
        email = request_json.get('email')
        password = request_json.get('password')
        name = request_json.get('name')
        
        result = asyncio.run(AuthManager.register_user(email, password, name))
        return result, 201
        
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': str(e)}, 500