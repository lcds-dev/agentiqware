# Agentiqware API Documentation v1.0

## Base URL
```
Production: https://api.agentiqware.com/v1
Staging: https://staging-api.agentiqware.com/v1
```

## Authentication
All API requests require authentication using JWT tokens.

### Headers
```http
Authorization: Bearer YOUR_JWT_TOKEN
Accept-Language: en|es  # Optional, defaults to en
Content-Type: application/json
```

## Rate Limiting
- **Free tier**: 100 requests/hour
- **Starter**: 1,000 requests/hour
- **Professional**: 10,000 requests/hour
- **Enterprise**: Unlimited

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "company": "Acme Corp",
  "language": "en"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "user_id": "user_1234567890",
    "email": "user@example.com",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Logout
```http
POST /auth/logout
```

---

## 📊 Flow Management Endpoints

### List Flows
```http
GET /flows
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20)
- `search` (string): Search query
- `status` (string): Filter by status (active|inactive|draft)
- `sort` (string): Sort field (created_at|updated_at|name)
- `order` (string): Sort order (asc|desc)

**Response:**
```json
{
  "status": "success",
  "data": {
    "flows": [
      {
        "id": "flow_abc123",
        "name": "Invoice Processing",
        "description": "Automated invoice processing workflow",
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:22:00Z",
        "last_execution": "2024-01-20T16:00:00Z",
        "execution_count": 156,
        "success_rate": 98.5
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 47,
      "pages": 3
    }
  }
}
```

### Get Flow Details
```http
GET /flows/{flow_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "flow_abc123",
    "name": "Invoice Processing",
    "description": "Automated invoice processing workflow",
    "status": "active",
    "nodes": [...],
    "connections": [...],
    "variables": {...},
    "settings": {...},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:22:00Z"
  }
}
```

### Create Flow
```http
POST /flows
```

**Request Body:**
```json
{
  "name": "New Automation Flow",
  "description": "Description of the flow",
  "nodes": [
    {
      "id": "node_1",
      "type": "trigger",
      "name": "Start",
      "position": {"x": 100, "y": 200},
      "config": {}
    }
  ],
  "connections": []
}
```

### Update Flow
```http
PUT /flows/{flow_id}
```

**Request Body:**
```json
{
  "name": "Updated Flow Name",
  "nodes": [...],
  "connections": [...]
}
```

### Delete Flow
```http
DELETE /flows/{flow_id}
```

### Duplicate Flow
```http
POST /flows/{flow_id}/duplicate
```

**Request Body:**
```json
{
  "name": "Copy of Invoice Processing"
}
```

---

## ⚡ Execution Endpoints

### Execute Flow
```http
POST /flows/{flow_id}/execute
```

**Request Body:**
```json
{
  "mode": "immediate|scheduled",
  "schedule": "0 */2 * * *",  // Optional, cron expression
  "variables": {
    "input_file": "/path/to/file.csv",
    "email_recipient": "admin@example.com"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "execution_id": "exec_xyz789",
    "flow_id": "flow_abc123",
    "status": "running",
    "started_at": "2024-01-20T16:00:00Z",
    "estimated_completion": "2024-01-20T16:02:00Z"
  }
}
```

### Get Execution Status
```http
GET /executions/{execution_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "execution_id": "exec_xyz789",
    "flow_id": "flow_abc123",
    "status": "completed",
    "started_at": "2024-01-20T16:00:00Z",
    "completed_at": "2024-01-20T16:01:45Z",
    "duration_ms": 105000,
    "nodes_executed": 12,
    "nodes_succeeded": 12,
    "nodes_failed": 0,
    "output": {...},
    "logs": [...]
  }
}
```

### Stop Execution
```http
POST /executions/{execution_id}/stop
```

### List Executions
```http
GET /executions
```

**Query Parameters:**
- `flow_id` (string): Filter by flow
- `status` (string): Filter by status (running|completed|failed)
- `from_date` (string): Start date (ISO 8601)
- `to_date` (string): End date (ISO 8601)

---

## 🤖 AI Generation Endpoints

### Generate Flow from Prompt
```http
POST /ai/generate-flow
```

**Request Body:**
```json
{
  "prompt": "Create a flow that monitors a folder for new Excel files, extracts data, and sends a summary email",
  "language": "en",
  "complexity": "simple|medium|advanced"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "flow_id": "flow_generated_123",
    "name": "Excel Monitor and Email Flow",
    "description": "Automatically generated flow based on your requirements",
    "nodes": [...],
    "connections": [...],
    "confidence_score": 0.92
  }
}
```

### Optimize Flow
```http
POST /ai/optimize-flow
```

**Request Body:**
```json
{
  "flow_id": "flow_abc123",
  "optimization_goals": ["performance", "cost", "reliability"]
}
```

---

## 📦 Component Endpoints

### List Available Components
```http
GET /components
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "components": [
      {
        "id": "file_search",
        "name": "File Search",
        "category": "File System",
        "description": "Search for files in a directory",
        "icon": "📁",
        "version": "1.0.0",
        "config_schema": {...}
      }
    ]
  }
}
```

### Get Component Details
```http
GET /components/{component_id}
```

---

## 🏪 Marketplace Endpoints

### Search Templates
```http
GET /marketplace/templates
```

**Query Parameters:**
- `search` (string): Search query
- `category` (string): Category filter
- `tags` (array): Tags filter
- `price_min` (number): Minimum price
- `price_max` (number): Maximum price
- `min_rating` (number): Minimum rating (1-5)

**Response:**
```json
{
  "status": "success",
  "data": {
    "templates": [
      {
        "id": "tpl_invoice_001",
        "name": "Invoice Processing Automation",
        "description": "Complete invoice processing workflow",
        "category": "finance",
        "tags": ["invoice", "OCR", "automation"],
        "author": "John Doe",
        "price": 29.99,
        "rating": 4.8,
        "downloads": 1250,
        "preview_image": "https://..."
      }
    ]
  }
}
```

### Install Template
```http
POST /marketplace/templates/{template_id}/install
```

**Request Body:**
```json
{
  "workspace_id": "ws_123",
  "configuration": {
    "invoice_folder": "/invoices",
    "email_recipient": "admin@company.com"
  }
}
```

### Publish Template
```http
POST /marketplace/templates/publish
```

**Request Body:**
```json
{
  "flow_id": "flow_abc123",
  "name": "My Awesome Template",
  "description": "This template does amazing things",
  "category": "productivity",
  "tags": ["automation", "productivity"],
  "price": 0,
  "documentation": "## How to use..."
}
```

---

## 📊 Analytics Endpoints

### Get Flow Analytics
```http
GET /analytics/flows/{flow_id}
```

**Query Parameters:**
- `period` (string): Time period (24h|7d|30d|custom)
- `from` (string): Start date (ISO 8601)
- `to` (string): End date (ISO 8601)

**Response:**
```json
{
  "status": "success",
  "data": {
    "flow_id": "flow_abc123",
    "period": "7d",
    "metrics": {
      "total_executions": 245,
      "successful_executions": 238,
      "failed_executions": 7,
      "success_rate": 97.14,
      "average_duration_ms": 1850,
      "total_cost": 12.45
    },
    "timeline": [...],
    "error_distribution": {...}
  }
}
```

### Get User Analytics
```http
GET /analytics/user
```

---

## 🔔 Webhook Configuration

### Register Webhook
```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["flow.executed", "flow.failed", "flow.completed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

#### flow.executed
```json
{
  "event": "flow.executed",
  "timestamp": "2024-01-20T16:00:00Z",
  "data": {
    "flow_id": "flow_abc123",
    "execution_id": "exec_xyz789",
    "status": "started"
  }
}
```

#### flow.completed
```json
{
  "event": "flow.completed",
  "timestamp": "2024-01-20T16:01:45Z",
  "data": {
    "flow_id": "flow_abc123",
    "execution_id": "exec_xyz789",
    "status": "completed",
    "duration_ms": 105000,
    "output": {...}
  }
}
```

#### flow.failed
```json
{
  "event": "flow.failed",
  "timestamp": "2024-01-20T16:01:45Z",
  "data": {
    "flow_id": "flow_abc123",
    "execution_id": "exec_xyz789",
    "error": {
      "code": "NODE_EXECUTION_ERROR",
      "message": "Failed to connect to database",
      "node_id": "node_5"
    }
  }
}
```

---

## 🔴 Error Responses

### Standard Error Format
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `AUTH_INVALID` | 401 | Invalid authentication token |
| `AUTH_EXPIRED` | 401 | Authentication token expired |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## 🧪 Testing Suite

### Python Test Examples

```python
import pytest
import requests
from datetime import datetime

class TestAgentiqwareAPI:
    BASE_URL = "https://api.agentiqware.com/v1"
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{self.BASE_URL}/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        token = response.json()["data"]["access_token"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_create_flow(self, auth_headers):
        """Test creating a new flow"""
        response = requests.post(
            f"{self.BASE_URL}/flows",
            headers=auth_headers,
            json={
                "name": f"Test Flow {datetime.now().isoformat()}",
                "description": "Automated test flow",
                "nodes": [
                    {
                        "id": "node_1",
                        "type": "trigger",
                        "name": "Start",
                        "position": {"x": 100, "y": 200}
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        assert response.json()["status"] == "success"
        assert "flow_" in response.json()["data"]["id"]
    
    def test_execute_flow(self, auth_headers):
        """Test executing a flow"""
        # First create a flow
        create_response = requests.post(
            f"{self.BASE_URL}/flows",
            headers=auth_headers,
            json={
                "name": "Execution Test Flow",
                "nodes": [{"id": "node_1", "type": "trigger"}]
            }
        )
        flow_id = create_response.json()["data"]["id"]
        
        # Execute the flow
        exec_response = requests.post(
            f"{self.BASE_URL}/flows/{flow_id}/execute",
            headers=auth_headers,
            json={"mode": "immediate"}
        )
        
        assert exec_response.status_code == 200
        assert "execution_id" in exec_response.json()["data"]
    
    def test_rate_limiting(self, auth_headers):
        """Test rate limiting"""
        responses = []
        
        # Make 150 requests (exceeding free tier limit)
        for _ in range(150):
            response = requests.get(
                f"{self.BASE_URL}/flows",
                headers=auth_headers
            )
            responses.append(response)
            
            if response.status_code == 429:
                break
        
        # Should hit rate limit
        assert any(r.status_code == 429 for r in responses)
    
    def test_i18n_support(self):
        """Test internationalization support"""
        # Test Spanish response
        response = requests.post(
            f"{self.BASE_URL}/auth/login",
            headers={"Accept-Language": "es"},
            json={
                "email": "invalid@example.com",
                "password": "wrong"
            }
        )
        
        assert response.json()["lang"] == "es"
        assert "Credenciales inválidas" in response.json()["message"]
```

### JavaScript/Node.js Test Examples

```javascript
const axios = require('axios');
const assert = require('assert');

describe('Agentiqware API Tests', () => {
  const BASE_URL = 'https://api.agentiqware.com/v1';
  let authToken = null;
  
  before(async () => {
    // Authenticate before tests
    const response = await axios.post(`${BASE_URL}/auth/login`, {
      email: 'test@example.com',
      password: 'TestPass123!'
    });
    authToken = response.data.data.access_token;
  });
  
  describe('Flow Management', () => {
    it('should list flows', async () => {
      const response = await axios.get(`${BASE_URL}/flows`, {
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      });
      
      assert.strictEqual(response.status, 200);
      assert.strictEqual(response.data.status, 'success');
      assert(Array.isArray(response.data.data.flows));
    });
    
    it('should create a new flow', async () => {
      const response = await axios.post(
        `${BASE_URL}/flows`,
        {
          name: 'Test Flow',
          nodes: [
            {
              id: 'node_1',
              type: 'trigger',
              name: 'Start'
            }
          ]
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        }
      );
      
      assert.strictEqual(response.status, 201);
      assert(response.data.data.id.startsWith('flow_'));
    });
  });
  
  describe('AI Generation', () => {
    it('should generate flow from prompt', async () => {
      const response = await axios.post(
        `${BASE_URL}/ai/generate-flow`,
        {
          prompt: 'Create a simple data processing flow',
          language: 'en'
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`
          }
        }
      );
      
      assert.strictEqual(response.status, 200);
      assert(response.data.data.nodes.length > 0);
    });
  });
});
```

### cURL Examples

```bash
# Authentication
curl -X POST https://api.agentiqware.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'

# Create Flow
curl -X POST https://api.agentiqware.com/v1/flows \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Flow","nodes":[{"id":"node_1","type":"trigger"}]}'

# Execute Flow
curl -X POST https://api.agentiqware.com/v1/flows/flow_abc123/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"immediate"}'

# Get Analytics
curl -X GET "https://api.agentiqware.com/v1/analytics/flows/flow_abc123?period=7d" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📦 SDKs

### Python SDK
```python
from agentiqware import AgentiqwareClient

client = AgentiqwareClient(api_key="your_api_key")

# Create a flow
flow = client.flows.create(
    name="My Automation",
    nodes=[...]
)

# Execute flow
execution = flow.execute(variables={"input": "data"})

# Wait for completion
result = execution.wait_for_completion()
print(result.output)
```

### JavaScript SDK
```javascript
const Agentiqware = require('@agentiqware/sdk');

const client = new Agentiqware({
  apiKey: 'your_api_key'
});

// Create and execute flow
const flow = await client.flows.create({
  name: 'My Automation',
  nodes: [...]
});

const execution = await flow.execute({
  variables: { input: 'data' }
});

const result = await execution.waitForCompletion();
console.log(result.output);
```

---

## 🔒 Security Best Practices

1. **Always use HTTPS** for API calls
2. **Store tokens securely** - Never commit tokens to version control
3. **Implement token rotation** - Refresh tokens regularly
4. **Use webhook secrets** - Verify webhook signatures
5. **Validate inputs** - Always validate user inputs
6. **Rate limit your requests** - Implement exponential backoff
7. **Monitor for anomalies** - Set up alerts for unusual activity

---

## 📞 Support

- **Documentation**: https://docs.agentiqware.com
- **Status Page**: https://status.agentiqware.com
- **Support Email**: support@agentiqware.com
- **Community Forum**: https://community.agentiqware.com
- **GitHub**: https://github.com/agentiqware