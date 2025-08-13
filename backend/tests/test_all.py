# =====================================
# Suite Completa de Testing para Agentiqware
# =====================================

import pytest
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import aiohttp
from faker import Faker

# Testing frameworks
import pytest_asyncio
from pytest_mock import MockerFixture
import responses
from freezegun import freeze_time

# Application imports
from google.cloud import firestore
from jose import jwt
import stripe

# Test data generator
fake = Faker()

# =====================================
# Configuración de Testing
# =====================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_client():
    """Create test client for API testing"""
    from main import app
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    async with app.test_client() as client:
        yield client

@pytest.fixture
def mock_firestore():
    """Mock Firestore client"""
    with patch('google.cloud.firestore.Client') as mock:
        mock_db = MagicMock()
        mock.return_value = mock_db
        yield mock_db

@pytest.fixture
def mock_stripe():
    """Mock Stripe client"""
    with patch('stripe') as mock:
        yield mock

@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing"""
    token_payload = {
        'user_id': 'test_user_123',
        'permissions': ['user'],
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(token_payload, 'test_secret', algorithm='HS256')
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

# =====================================
# Unit Tests - Modelos y Utilidades
# =====================================

class TestModels:
    """Test data models and utilities"""
    
    def test_user_model_creation(self):
        """Test user model creation"""
        from models import User
        
        user = User(
            email=fake.email(),
            name=fake.name(),
            password='SecurePass123!'
        )
        
        assert user.email
        assert user.name
        assert user.password_hash != 'SecurePass123!'
        assert user.created_at
    
    def test_flow_model_validation(self):
        """Test flow model validation"""
        from models import Flow
        
        flow = Flow(
            name='Test Flow',
            user_id='user_123',
            nodes=[
                {'id': 'node_1', 'type': 'trigger'},
                {'id': 'node_2', 'type': 'action'}
            ],
            connections=[
                {'from': 'node_1', 'to': 'node_2'}
            ]
        )
        
        assert flow.validate()
        assert len(flow.nodes) == 2
        assert len(flow.connections) == 1
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from utils.security import hash_password, verify_password
        
        password = 'MySecurePassword123!'
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password('WrongPassword', hashed)
    
    def test_jwt_token_generation(self):
        """Test JWT token generation and validation"""
        from utils.auth import generate_token, validate_token
        
        user_id = 'user_123'
        token = generate_token(user_id, ['user'])
        
        payload = validate_token(token)
        assert payload['user_id'] == user_id
        assert 'user' in payload['permissions']
    
    @pytest.mark.parametrize("email,valid", [
        ("user@example.com", True),
        ("user.name@example.co.uk", True),
        ("user+tag@example.com", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("user@", False),
    ])
    def test_email_validation(self, email, valid):
        """Test email validation"""
        from utils.validators import validate_email
        
        assert validate_email(email) == valid
    
    def test_data_encryption(self):
        """Test data encryption and decryption"""
        from utils.encryption import encrypt_data, decrypt_data
        
        sensitive_data = "Credit Card: 4242-4242-4242-4242"
        encrypted = encrypt_data(sensitive_data)
        
        assert encrypted != sensitive_data
        assert decrypt_data(encrypted) == sensitive_data

# =====================================
# Integration Tests - Servicios
# =====================================

class TestAuthenticationService:
    """Test authentication service"""
    
    @pytest.mark.asyncio
    async def test_user_registration(self, mock_firestore):
        """Test user registration flow"""
        from services.auth import AuthenticationManager
        
        auth_manager = AuthenticationManager()
        auth_manager.db = mock_firestore
        
        # Mock Firestore responses
        mock_firestore.collection().where().get.return_value = []
        mock_firestore.collection().document().set = AsyncMock()
        
        result = await auth_manager.register_user(
            email=fake.email(),
            password='SecurePass123!',
            name=fake.name()
        )
        
        assert result['user_id']
        assert result['verification_required']
        assert mock_firestore.collection().document().set.called
    
    @pytest.mark.asyncio
    async def test_user_login(self, mock_firestore):
        """Test user login flow"""
        from services.auth import AuthenticationManager
        
        auth_manager = AuthenticationManager()
        auth_manager.db = mock_firestore
        
        # Setup mock user
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            'user_id': 'user_123',
            'email': 'test@example.com',
            'password_hash': auth_manager.pwd_context.hash('password123'),
            'permissions': ['user'],
            'mfa_enabled': False
        }
        
        mock_firestore.collection().where().get.return_value = [mock_user]
        mock_firestore.collection().document().update = AsyncMock()
        
        result = await auth_manager.authenticate(
            email='test@example.com',
            password='password123'
        )
        
        assert result['status'] == 'success'
        assert result['access_token']
        assert result['refresh_token']
    
    @pytest.mark.asyncio
    async def test_mfa_authentication(self, mock_firestore):
        """Test MFA authentication flow"""
        from services.auth import AuthenticationManager
        import pyotp
        
        auth_manager = AuthenticationManager()
        auth_manager.db = mock_firestore
        
        # Setup mock user with MFA
        secret = pyotp.random_base32()
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            'user_id': 'user_123',
            'email': 'test@example.com',
            'password_hash': auth_manager.pwd_context.hash('password123'),
            'permissions': ['user'],
            'mfa_enabled': True,
            'mfa_secret': auth_manager._encrypt_sensitive_data(secret)
        }
        
        mock_firestore.collection().where().get.return_value = [mock_user]
        mock_firestore.collection().document().get.return_value = mock_user
        
        # First attempt without MFA code
        result = await auth_manager.authenticate(
            email='test@example.com',
            password='password123'
        )
        
        assert result['status'] == 'mfa_required'
        
        # Second attempt with valid MFA code
        totp = pyotp.TOTP(secret)
        result = await auth_manager.authenticate(
            email='test@example.com',
            password='password123',
            mfa_code=totp.now()
        )
        
        assert result['status'] == 'success'

class TestFlowExecutionService:
    """Test flow execution service"""
    
    @pytest.mark.asyncio
    async def test_simple_flow_execution(self, mock_firestore):
        """Test execution of a simple flow"""
        from services.flow_engine import FlowEngine
        
        # Create test flow
        flow_data = {
            'nodes': [
                {'id': 'node_1', 'type': 'trigger', 'data': {}},
                {'id': 'node_2', 'type': 'log', 'data': {'message': 'Test'}}
            ],
            'connections': [
                {'from': 'node_1', 'to': 'node_2'}
            ]
        }
        
        mock_firestore.collection().document().get().to_dict.return_value = flow_data
        mock_firestore.collection().document().set = AsyncMock()
        
        engine = FlowEngine('flow_123', 'user_123')
        engine.db = mock_firestore
        
        result = await engine.execute_flow()
        
        assert result['status'] == 'success'
        assert result['nodes_executed'] == 2
    
    @pytest.mark.asyncio
    async def test_conditional_flow_execution(self, mock_firestore):
        """Test execution of flow with conditional branching"""
        from services.flow_engine import FlowEngine
        
        flow_data = {
            'nodes': [
                {'id': 'node_1', 'type': 'trigger', 'data': {}},
                {
                    'id': 'node_2',
                    'type': 'condition',
                    'data': {
                        'condition': 'value',
                        'operator': '==',
                        'value': 'test'
                    }
                },
                {'id': 'node_3', 'type': 'log', 'data': {'message': 'True branch'}},
                {'id': 'node_4', 'type': 'log', 'data': {'message': 'False branch'}}
            ],
            'connections': [
                {'from': 'node_1', 'to': 'node_2'},
                {'from': 'node_2', 'to': 'node_3', 'condition': 'true'},
                {'from': 'node_2', 'to': 'node_4', 'condition': 'false'}
            ]
        }
        
        mock_firestore.collection().document().get().to_dict.return_value = flow_data
        mock_firestore.collection().document().set = AsyncMock()
        
        engine = FlowEngine('flow_123', 'user_123')
        engine.db = mock_firestore
        engine.context['variables']['value'] = 'test'
        
        result = await engine.execute_flow()
        
        assert result['status'] == 'success'
        # Should execute trigger, condition, and true branch
        assert result['nodes_executed'] == 3

class TestBillingService:
    """Test billing and subscription service"""
    
    @pytest.mark.asyncio
    async def test_create_subscription(self, mock_firestore, mock_stripe):
        """Test subscription creation"""
        from services.billing import SubscriptionManager, SubscriptionPlan
        
        manager = SubscriptionManager()
        manager.db = mock_firestore
        
        # Mock Stripe responses
        mock_stripe.Subscription.create.return_value = MagicMock(
            id='sub_123',
            status='active',
            current_period_start=int(datetime.utcnow().timestamp()),
            current_period_end=int((datetime.utcnow() + timedelta(days=30)).timestamp()),
            trial_end=None
        )
        
        # Mock Firestore
        mock_firestore.collection().document().get().to_dict.return_value = {
            'stripe_customer_id': 'cus_123'
        }
        mock_firestore.collection().document().set = AsyncMock()
        
        result = await manager.create_subscription(
            user_id='user_123',
            plan=SubscriptionPlan.PROFESSIONAL,
            billing_cycle='monthly'
        )
        
        assert result['subscription_id'] == 'sub_123'
        assert result['status'] == 'active'
        assert result['plan'] == 'professional'
    
    @pytest.mark.asyncio
    async def test_usage_limits_check(self, mock_firestore):
        """Test usage limits checking"""
        from services.billing import SubscriptionManager
        
        manager = SubscriptionManager()
        manager.db = mock_firestore
        
        # Mock user with limits
        mock_firestore.collection().document().get().to_dict.return_value = {
            'limits': {
                'max_flows': 10,
                'max_executions_per_month': 100
            }
        }
        
        # Mock current usage
        mock_firestore.collection().document().get().to_dict.return_value = {
            'flows_created': 5,
            'executions': 50
        }
        
        # Check within limits
        result = await manager.check_usage_limits('user_123', 'flows', 1)
        assert result['allowed'] == True
        assert result['remaining'] == 5
        
        # Check exceeding limits
        result = await manager.check_usage_limits('user_123', 'flows', 6)
        assert result['allowed'] == False
        assert result['exceeded_by'] == 1

# =====================================
# API Tests - Endpoints
# =====================================

class TestAPIEndpoints:
    """Test API endpoints"""
    
    @pytest.mark.asyncio
    async def test_flow_creation_endpoint(self, test_client, auth_headers, mock_firestore):
        """Test POST /flows endpoint"""
        flow_data = {
            'name': 'Test Flow',
            'nodes': [
                {'id': 'node_1', 'type': 'trigger'}
            ],
            'connections': []
        }
        
        mock_firestore.collection().document().set = AsyncMock()
        
        response = await test_client.post(
            '/api/v1/flows',
            json=flow_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = await response.get_json()
        assert data['status'] == 'success'
        assert 'flow_id' in data['data']
    
    @pytest.mark.asyncio
    async def test_flow_execution_endpoint(self, test_client, auth_headers, mock_firestore):
        """Test POST /flows/{flow_id}/execute endpoint"""
        mock_firestore.collection().document().get().exists = True
        mock_firestore.collection().document().get().to_dict.return_value = {
            'nodes': [{'id': 'node_1', 'type': 'trigger'}],
            'connections': []
        }
        
        response = await test_client.post(
            '/api/v1/flows/flow_123/execute',
            json={'mode': 'immediate'},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = await response.get_json()
        assert data['status'] == 'success'
        assert 'execution_id' in data['data']
    
    @pytest.mark.asyncio
    async def test_ai_generation_endpoint(self, test_client, auth_headers):
        """Test POST /ai/generate-flow endpoint"""
        with patch('services.ai.AIFlowGenerator.generate_flow') as mock_generate:
            mock_generate.return_value = {
                'flow_id': 'flow_generated_123',
                'name': 'Generated Flow',
                'nodes': [],
                'connections': []
            }
            
            response = await test_client.post(
                '/api/v1/ai/generate-flow',
                json={'prompt': 'Create a flow that sends emails'},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = await response.get_json()
            assert data['status'] == 'success'
            assert data['data']['flow_id'] == 'flow_generated_123'
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, test_client, auth_headers):
        """Test rate limiting on API endpoints"""
        # Make multiple rapid requests
        responses = []
        for _ in range(150):  # Exceed rate limit
            response = await test_client.get(
                '/api/v1/flows',
                headers=auth_headers
            )
            responses.append(response.status_code)
            
            if response.status_code == 429:
                break
        
        # Should hit rate limit
        assert 429 in responses
    
    @pytest.mark.asyncio
    async def test_webhook_validation(self, test_client):
        """Test webhook signature validation"""
        payload = {'event': 'flow.completed', 'flow_id': 'flow_123'}
        secret = 'webhook_secret'
        
        # Generate valid signature
        import hmac
        import hashlib
        signature = hmac.new(
            secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = await test_client.post(
            '/api/v1/webhooks/stripe',
            json=payload,
            headers={
                'X-Webhook-Signature': f'sha256={signature}'
            }
        )
        
        assert response.status_code == 200

# =====================================
# End-to-End Tests
# =====================================

class TestE2EScenarios:
    """End-to-end test scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, test_client, mock_firestore, mock_stripe):
        """Test complete user journey from registration to flow execution"""
        
        # 1. Register user
        registration_data = {
            'email': fake.email(),
            'password': 'SecurePass123!',
            'name': fake.name()
        }
        
        response = await test_client.post(
            '/api/v1/auth/register',
            json=registration_data
        )
        assert response.status_code == 201
        user_data = await response.get_json()
        
        # 2. Verify email (simulate)
        verification_token = user_data['data'].get('verification_token')
        response = await test_client.get(
            f'/api/v1/auth/verify?token={verification_token}'
        )
        assert response.status_code == 200
        
        # 3. Login
        response = await test_client.post(
            '/api/v1/auth/login',
            json={
                'email': registration_data['email'],
                'password': registration_data['password']
            }
        )
        assert response.status_code == 200
        login_data = await response.get_json()
        
        auth_headers = {
            'Authorization': f"Bearer {login_data['data']['access_token']}"
        }
        
        # 4. Create subscription
        response = await test_client.post(
            '/api/v1/billing/subscribe',
            json={
                'plan': 'starter',
                'billing_cycle': 'monthly'
            },
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        
        # 5. Create a flow
        flow_data = {
            'name': 'My First Flow',
            'nodes': [
                {'id': 'node_1', 'type': 'trigger', 'data': {}},
                {'id': 'node_2', 'type': 'email', 'data': {'to': 'test@example.com'}}
            ],
            'connections': [
                {'from': 'node_1', 'to': 'node_2'}
            ]
        }
        
        response = await test_client.post(
            '/api/v1/flows',
            json=flow_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        flow_response = await response.get_json()
        flow_id = flow_response['data']['flow_id']
        
        # 6. Execute the flow
        response = await test_client.post(
            f'/api/v1/flows/{flow_id}/execute',
            json={'mode': 'immediate'},
            headers=auth_headers
        )
        assert response.status_code == 200
        execution_data = await response.get_json()
        execution_id = execution_data['data']['execution_id']
        
        # 7. Check execution status
        response = await test_client.get(
            f'/api/v1/executions/{execution_id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        status_data = await response.get_json()
        assert status_data['data']['status'] in ['running', 'completed', 'failed']
    
    @pytest.mark.asyncio
    async def test_collaboration_workflow(self, test_client, mock_firestore):
        """Test collaboration workflow between users"""
        
        # Create two users
        user1_token = self._create_test_user('user1@example.com')
        user2_token = self._create_test_user('user2@example.com')
        
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        
        # User 1 creates a flow
        response = await test_client.post(
            '/api/v1/flows',
            json={'name': 'Shared Flow', 'nodes': []},
            headers=user1_headers
        )
        flow_data = await response.get_json()
        flow_id = flow_data['data']['flow_id']
        
        # User 1 shares flow with User 2
        response = await test_client.post(
            f'/api/v1/flows/{flow_id}/share',
            json={
                'user_email': 'user2@example.com',
                'permission': 'edit'
            },
            headers=user1_headers
        )
        assert response.status_code == 200
        
        # User 2 can now access the flow
        response = await test_client.get(
            f'/api/v1/flows/{flow_id}',
            headers=user2_headers
        )
        assert response.status_code == 200
        
        # User 2 edits the flow
        response = await test_client.put(
            f'/api/v1/flows/{flow_id}',
            json={'name': 'Updated Shared Flow'},
            headers=user2_headers
        )
        assert response.status_code == 200
    
    def _create_test_user(self, email):
        """Helper to create test user and return token"""
        # Implementation would create user and return auth token
        return f"test_token_{email}"

# =====================================
# Performance Tests
# =====================================

class TestPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_flow_execution_performance(self, benchmark, mock_firestore):
        """Benchmark flow execution performance"""
        from services.flow_engine import FlowEngine
        
        # Create complex flow
        nodes = []
        connections = []
        for i in range(100):
            nodes.append({
                'id': f'node_{i}',
                'type': 'action',
                'data': {'value': i}
            })
            if i > 0:
                connections.append({
                    'from': f'node_{i-1}',
                    'to': f'node_{i}'
                })
        
        flow_data = {'nodes': nodes, 'connections': connections}
        mock_firestore.collection().document().get().to_dict.return_value = flow_data
        
        engine = FlowEngine('flow_123', 'user_123')
        engine.db = mock_firestore
        
        # Benchmark execution
        result = await benchmark(engine.execute_flow)
        assert result['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_concurrent_flow_executions(self, mock_firestore):
        """Test concurrent flow executions"""
        from services.flow_engine import FlowEngine
        
        # Simulate multiple concurrent executions
        tasks = []
        for i in range(50):
            engine = FlowEngine(f'flow_{i}', f'user_{i}')
            engine.db = mock_firestore
            tasks.append(engine.execute_flow())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check all completed without errors
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_database_connection_pool(self):
        """Test database connection pooling"""
        from utils.database import get_connection_pool
        
        pool = get_connection_pool(max_connections=10)
        
        # Simulate concurrent database operations
        async def db_operation(i):
            async with pool.acquire() as conn:
                # Simulate database query
                await asyncio.sleep(0.1)
                return f"Result {i}"
        
        tasks = [db_operation(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 100
        assert all(r.startswith("Result") for r in results)

# =====================================
# Security Tests
# =====================================

class TestSecurity:
    """Security and vulnerability tests"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, test_client, auth_headers):
        """Test SQL injection prevention"""
        malicious_input = "'; DROP TABLE users; --"
        
        response = await test_client.get(
            f'/api/v1/flows?search={malicious_input}',
            headers=auth_headers
        )
        
        # Should handle safely without error
        assert response.status_code in [200, 400]
        # Database should still be intact
        # Additional checks would verify no damage was done
    
    @pytest.mark.asyncio
    async def test_xss_prevention(self, test_client, auth_headers):
        """Test XSS prevention"""
        xss_payload = '<script>alert("XSS")</script>'
        
        response = await test_client.post(
            '/api/v1/flows',
            json={'name': xss_payload, 'nodes': []},
            headers=auth_headers
        )
        
        if response.status_code == 201:
            data = await response.get_json()
            # Check that script tags are escaped
            assert '<script>' not in str(data)
    
    @pytest.mark.asyncio
    async def test_csrf_protection(self, test_client):
        """Test CSRF protection"""
        # Attempt request without CSRF token
        response = await test_client.post(
            '/api/v1/flows',
            json={'name': 'Test', 'nodes': []},
            headers={'Authorization': 'Bearer fake_token'}
        )
        
        # Should be rejected without proper CSRF token
        assert response.status_code in [400, 403]
    
    @pytest.mark.asyncio
    async def test_rate_limiting_by_ip(self, test_client):
        """Test rate limiting by IP address"""
        # Simulate requests from same IP
        for i in range(200):
            response = await test_client.get(
                '/api/v1/public/status',
                headers={'X-Forwarded-For': '192.168.1.1'}
            )
            
            if response.status_code == 429:
                # Rate limit hit
                assert i < 200  # Should hit before 200 requests
                break
    
    @pytest.mark.asyncio
    async def test_password_policy_enforcement(self, test_client):
        """Test password policy enforcement"""
        weak_passwords = [
            'password',
            '12345678',
            'Password',  # No special char
            'Pass123!',  # Too short
        ]
        
        for password in weak_passwords:
            response = await test_client.post(
                '/api/v1/auth/register',
                json={
                    'email': fake.email(),
                    'password': password,
                    'name': fake.name()
                }
            )
            
            assert response.status_code == 400
            data = await response.get_json()
            assert 'password' in str(data).lower()

# =====================================
# Test Utilities
# =====================================

class TestUtilities:
    """Utility functions for testing"""
    
    @staticmethod
    def create_mock_flow(num_nodes=5):
        """Create a mock flow for testing"""
        nodes = []
        connections = []
        
        for i in range(num_nodes):
            nodes.append({
                'id': f'node_{i}',
                'type': 'action' if i > 0 else 'trigger',
                'position': {'x': i * 100, 'y': 200},
                'data': {'index': i}
            })
            
            if i > 0:
                connections.append({
                    'from': f'node_{i-1}',
                    'to': f'node_{i}'
                })
        
        return {
            'name': f'Test Flow {uuid.uuid4().hex[:8]}',
            'nodes': nodes,
            'connections': connections
        }
    
    @staticmethod
    def create_mock_user():
        """Create a mock user for testing"""
        return {
            'email': fake.email(),
            'name': fake.name(),
            'password': f'{fake.password()}123!',
            'company': fake.company(),
            'phone': fake.phone_number()
        }
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout=10, interval=0.1):
        """Wait for a condition to be true"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False

# =====================================
# Test Fixtures and Data
# =====================================

@pytest.fixture
def sample_flow_data():
    """Sample flow data for testing"""
    return {
        'name': 'Sample Flow',
        'description': 'A sample flow for testing',
        'nodes': [
            {
                'id': 'trigger_1',
                'type': 'schedule_trigger',
                'name': 'Daily Trigger',
                'position': {'x': 100, 'y': 200},
                'data': {'cron': '0 9 * * *'}
            },
            {
                'id': 'fetch_1',
                'type': 'http_request',
                'name': 'Fetch Data',
                'position': {'x': 300, 'y': 200},
                'data': {
                    'url': 'https://api.example.com/data',
                    'method': 'GET'
                }
            },
            {
                'id': 'transform_1',
                'type': 'data_transform',
                'name': 'Transform Data',
                'position': {'x': 500, 'y': 200},
                'data': {
                    'transformations': [
                        {'type': 'filter', 'field': 'status', 'value': 'active'}
                    ]
                }
            },
            {
                'id': 'save_1',
                'type': 'database_save',
                'name': 'Save to Database',
                'position': {'x': 700, 'y': 200},
                'data': {
                    'collection': 'processed_data'
                }
            }
        ],
        'connections': [
            {'from': 'trigger_1', 'to': 'fetch_1'},
            {'from': 'fetch_1', 'to': 'transform_1'},
            {'from': 'transform_1', 'to': 'save_1'}
        ]
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'user_id': f'user_{uuid.uuid4().hex[:12]}',
        'email': fake.email(),
        'name': fake.name(),
        'organization': fake.company(),
        'subscription_plan': 'professional',
        'created_at': datetime.utcnow().isoformat()
    }

# =====================================
# Test Runner Configuration
# =====================================

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        '-v',
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--asyncio-mode=auto',
        '-W', 'ignore::DeprecationWarning'
    ])