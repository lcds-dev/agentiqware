# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agentiqware is a SaaS platform for creating, editing, and executing digital agents and RPA processes. The platform consists of a React frontend with TypeScript, a Python FastAPI backend using Google Cloud Functions, and infrastructure deployed on Google Cloud Platform.

## Architecture

- **Frontend**: React 19 with TypeScript, hosted on Firebase
- **Backend**: Python 3.11 with FastAPI, deployed as Google Cloud Functions  
- **Database**: Firestore (primary) + Redis (caching)
- **Infrastructure**: Google Cloud Platform with Terraform
- **AI Integration**: Anthropic Claude API for flow generation
- **Payment Processing**: Stripe integration

## Development Commands

### Frontend (React)
```bash
cd frontend
npm install          # Install dependencies
npm start           # Start development server (port 3000)
npm run build       # Build for production
npm test            # Run tests with coverage
```

### Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py      # Start development server (port 8080)
```

### Testing
```bash
./scripts/run-tests.sh  # Run all tests (frontend + backend)
```

### Infrastructure
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

### Deployment
```bash
./scripts/deploy.sh  # Deploy to production
```

### Docker Development Environment
```bash
docker-compose up -d  # Start all services (frontend, backend, redis, firestore)
```

## Key Architecture Components

### Frontend Structure
- `src/components/FlowEditor.tsx` - Visual drag-and-drop flow editor
- `src/components/AdminPanel.tsx` - Administration interface
- `src/components/RealTimeMonitoring.tsx` - Execution monitoring dashboard

### Backend Services
- `backend/services/flow_engine.py` - Core flow execution engine
- `backend/services/billing.py` - Stripe integration and subscription management
- `backend/services/rpa.py` - RPA automation capabilities
- `backend/services/security.py` - Authentication and authorization
- `backend/services/notifications.py` - Multi-channel notifications

### Cloud Functions
- `backend/functions/auth/` - Authentication handlers
- `backend/functions/flows/` - Flow management and execution
- `backend/functions/billing/` - Payment processing
- `backend/functions/rpa/` - RPA execution workers
- `backend/functions/notifications/` - Notification services

## Data Models

### Core Entities (Firestore Collections)
- `users` - User accounts and profiles
- `flows` - Flow definitions and metadata
- `executions` - Execution logs and results
- `components` - Reusable flow components
- `templates` - Flow templates for marketplace

## Development Guidelines

### Code Quality
The project uses:
- **Python**: Black formatter, Flake8 linter, MyPy for type checking, Pylint for code analysis
- **React**: ESLint with react-app configuration
- **Testing**: Pytest for backend (with coverage), React Testing Library for frontend

### Environment Configuration
- Development environment uses Docker Compose with Firestore emulator
- Production uses Google Cloud Platform services
- Environment variables are managed through .env files (not committed)

### Security Considerations
- Authentication via OAuth 2.0 with multiple providers
- RBAC (Role-Based Access Control) implementation
- Secrets managed through Google Secret Manager
- All API endpoints require authentication except health checks

### RPA Capabilities
The platform includes advanced RPA automation:
- Screen automation with PyAutoGUI and Pynput
- OCR capabilities with Tesseract
- Computer Vision with OpenCV
- Web scraping with Selenium and BeautifulSoup
- Document processing (PDF, Excel) with specialized libraries

### AI Integration
- Flow generation from natural language prompts via Anthropic Claude API
- Intelligent optimization suggestions for flows
- Component recommendations based on usage patterns

## Common Development Workflows

### Adding New Components
1. Define component schema in JSON format
2. Implement backend handler in `backend/services/`
3. Add frontend integration in flow editor
4. Update component registry and documentation

### Creating Cloud Functions
1. Create function directory under `backend/functions/`
2. Implement handler with proper error handling and logging
3. Add deployment configuration in `scripts/deploy.sh`
4. Test locally with functions framework

### Database Schema Changes
1. Update Firestore security rules if needed
2. Create migration scripts in `backend/migrations/`
3. Update Terraform configuration for any required indexes
4. Test with development environment first

### Infrastructure Changes
1. Modify `infrastructure/main.tf` for resource changes
2. Plan and apply changes using Terraform
3. Update monitoring and alerting rules as needed
4. Document changes for team visibility

## Monitoring and Observability

- Google Cloud Monitoring for infrastructure metrics
- Custom metrics for business KPIs (execution success rate, user engagement)
- Structured logging throughout the application
- Error tracking and alerting configured via Cloud Functions
- Performance monitoring for both frontend and backend components