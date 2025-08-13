#!/bin/bash

echo "🚀 Iniciando Agentiqware en modo desarrollo..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Iniciar servicios con Docker Compose
docker-compose up -d

echo "✅ Servicios iniciados:"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo ""
echo "Para ver los logs: docker-compose logs -f"
echo "Para detener: docker-compose down"
