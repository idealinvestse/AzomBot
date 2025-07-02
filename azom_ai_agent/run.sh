#!/bin/bash

# AZOM AI Agent - Run Script
# This script helps start the application in development mode

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a process is running
is_running() {
    if command_exists pgrep; then
        pgrep -f "$1" > /dev/null
    else
        ps aux | grep -v grep | grep "$1" > /dev/null
    fi
    return $?
}

# Function to start the backend
start_backend() {
    echo -e "${YELLOW}Starting backend server...${NC}"
    cd "$(dirname "$0")"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        if [ "$OS" = "Windows_NT" ]; then
            .\\venv\\Scripts\\activate
        else
            source venv/bin/activate
        fi
    fi
    
    # Install Python dependencies if needed
    if [ ! -d "venv" ] || [ ! -f "venv/pyvenv.cfg" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python -m venv venv
        if [ "$OS" = "Windows_NT" ]; then
            .\\venv\\Scripts\\activate
        else
            source venv/bin/activate
        fi
        pip install -r requirements.txt
    fi
    
    # Start the FastAPI server
    alembic upgrade head
    UVICORN=${UVICORN:-uvicorn}
    PIPELINE_PORT=${PIPELINE_PORT:-8001}
    API_PORT=${API_PORT:-8000}
    $UVICORN app.pipelineserver.pipeline_app.main:app --reload --port "$PIPELINE_PORT" &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend server started (PID: $BACKEND_PID)${NC}"
    echo -e "${GREEN}API Documentation: http://localhost:$API_PORT/docs${NC}"
}

# Function to start the frontend
start_frontend() {
    echo -e "${YELLOW}Starting frontend development server...${NC}"
    cd "app/pipelineserver/pipeline_app/admin/frontend" 2>/dev/null || {
        echo -e "${YELLOW}Frontend directory not found. Skipping frontend...${NC}"
        return 1
    }
    
    # Check if Node.js is installed
    if ! command_exists npm; then
        echo -e "${YELLOW}npm not found. Please install Node.js to run the frontend.${NC}"
        return 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    # Start the frontend dev server
    npm run dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend server started (PID: $FRONTEND_PID)${NC}"
    echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
    cd ../../../../..
}

# Main execution
main() {
    # Detect OS
    case "$(uname -s)" in
        Linux*)     OS=Linux;;
        Darwin*)    OS=Mac;;
        CYGWIN*|MINGW*|MSYS*) OS=Windows_NT;;
        *)          OS=Unknown
    esac
    
    # Check for required commands
    for cmd in python pip; do
        if ! command_exists "$cmd"; then
            echo "Error: $cmd is not installed"
            exit 1
        fi
    done
    
    # Start services
    start_backend
    start_frontend
    
    # Wait for user to press Ctrl+C
    echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Setup trap to kill background processes on script exit
    trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT
    
    # Keep script running
    wait
}

# Run the main function
main "$@"
