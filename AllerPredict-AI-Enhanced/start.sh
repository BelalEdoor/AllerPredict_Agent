#!/bin/bash

# AllerPredict AI - Quick Start Script
# This script sets up and runs the entire system

echo "🚀 AllerPredict AI - Starting System..."
echo "======================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama is not installed!${NC}"
    echo "Please install Ollama from: https://ollama.ai"
    exit 1
fi

echo -e "${GREEN}✅ Ollama detected${NC}"

# Check if Llama model is available
if ! ollama list | grep -q "llama3.2"; then
    echo -e "${BLUE}📥 Downloading Llama 3.2 model...${NC}"
    ollama pull llama3.2
fi

echo -e "${GREEN}✅ Llama 3.2 model ready${NC}"

# Backend Setup
echo -e "${BLUE}🔧 Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Start Backend in background
echo -e "${BLUE}🌐 Starting Backend Server...${NC}"
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Frontend Setup
echo -e "${BLUE}🎨 Setting up Frontend...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
fi

echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Start Frontend
echo -e "${BLUE}🚀 Starting Frontend...${NC}"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ System is running!${NC}"
echo "======================================"
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo -e "${BLUE}🛑 Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
