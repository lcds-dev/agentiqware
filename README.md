# 🚀 Agentiqware - RPA & Digital Agents Platform

## 📋 Descripción

Agentiqware es una plataforma SaaS completa para la creación, edición y ejecución de agentes digitales y procesos RPA.

## 🛠️ Stack Tecnológico

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, Google Cloud Functions
- **Database**: Firestore, Redis
- **Infrastructure**: Google Cloud Platform, Docker, Kubernetes
- **AI**: Anthropic Claude, Google Vision API

## 🚀 Inicio Rápido

### Requisitos Previos

- Node.js 18+
- Python 3.11+
- Docker y Docker Compose
- Google Cloud SDK
- Cuenta de Google Cloud Platform

### Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuempresa/agentiqware.git
cd agentiqware
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

3. Iniciar entorno de desarrollo:
```bash
./scripts/dev.sh
```

4. Acceder a la aplicación:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- Documentación API: http://localhost:8080/docs

## 📦 Estructura del Proyecto

```
agentiqware/
├── frontend/           # Aplicación React
├── backend/           # API y servicios Python
├── infrastructure/    # Configuración de infraestructura
├── database/         # Esquemas y migraciones
├── docs/            # Documentación
└── scripts/         # Scripts de utilidad
```

## 🔧 Comandos Útiles

```bash
# Desarrollo
npm run dev          # Iniciar frontend en desarrollo
python main.py       # Iniciar backend en desarrollo

# Testing
npm test            # Tests frontend
pytest              # Tests backend

# Build
npm run build       # Build frontend
docker-compose build # Build containers

# Deploy
./scripts/deploy.sh  # Deploy a producción
```

## 📚 Documentación

- [Documentación de API](docs/api/README.md)
- [Guía de Usuario](docs/user/README.md)
- [Arquitectura Técnica](docs/technical/README.md)
- [Guía de Contribución](CONTRIBUTING.md)

## 📄 Licencia

Copyright (c) 2024 Agentiqware. Todos los derechos reservados.

## 🤝 Soporte

- Email: support@agentiqware.com
- Documentation: https://docs.agentiqware.com
- Status: https://status.agentiqware.com
