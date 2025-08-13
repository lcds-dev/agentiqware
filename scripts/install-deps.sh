#!/bin/bash

echo "📦 Instalando dependencias..."

# Frontend
echo "Installing frontend dependencies..."
cd frontend
npm install

# Backend
echo "Installing backend dependencies..."
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Dependencias instaladas"
