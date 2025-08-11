#!/bin/bash
# Iniciar entorno de desarrollo local

echo "Starting Agentiqware development environment..."

# Start Docker services
docker-compose up -d redis firestore-emulator

# Start backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# Start frontend
cd ../frontend
npm install
npm start
