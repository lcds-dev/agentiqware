#!/bin/bash

echo "🧪 Ejecutando tests..."

# Frontend tests
echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false

# Backend tests
echo "Running backend tests..."
cd ../backend
source venv/bin/activate
pytest tests/ -v --cov=. --cov-report=html

echo "✅ Tests completados"
echo "Coverage report: backend/htmlcov/index.html"
