# 🚀 Agentiqware - RPA & Digital Agents Platform

## 📋 Descripción
Agentiqware es una plataforma SaaS completa para la creación, edición y ejecución de agentes digitales y procesos RPA.

## 🛠️ Stack Tecnológico
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI + Google Cloud Functions
- **Database**: Firestore + Redis
- **Infrastructure**: Google Cloud Platform + Terraform
- **AI**: Anthropic Claude API

## 🚀 Instalación Rápida

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- Google Cloud SDK
- Docker
- Terraform

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tuempresa/agentiqware.git
cd agentiqware
```

2. **Instalar dependencias del Frontend**
```bash
cd frontend
npm install
```

3. **Instalar dependencias del Backend**
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Iniciar en desarrollo**
```bash
# Terminal 1 - Frontend
cd frontend
npm run dev

# Terminal 2 - Backend
cd backend
python main.py
```

## 📚 Documentación
- [Documentación Técnica](docs/technical/README.md)
- [API Reference](docs/api/README.md)
- [Guía de Usuario](docs/user/README.md)

## 📄 Licencia
Copyright © 2024 Agentiqware. Todos los derechos reservados.
