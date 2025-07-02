@echo off
:: AZOM AI Agent - Run Script for Windows
:: This script helps start the application in development mode

title AZOM AI Agent - Development Server
color 0A

echo =======================================
echo   AZOM AI Agent - Development Setup
echo =======================================
echo.

:: Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if virtual environment exists, create if not
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo Installing/updating Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

:: Start the backend server
echo.
echo Starting Backend Server...
start "AZOM Backend" cmd /k "title AZOM Backend && call venv\Scripts\activate && uvicorn app.pipelineserver.pipeline_app.main:app --reload --port 8000"

:: Check if frontend directory exists
if exist "app\pipelineserver\pipeline_app\admin\frontend\" (
    cd "app\pipelineserver\pipeline_app\admin\frontend"
    
    :: Check if node_modules exists
    if not exist "node_modules\" (
        echo Installing frontend dependencies...
        call npm install
        if %ERRORLEVEL% neq 0 (
            echo [WARNING] Failed to install frontend dependencies
        )
    )
    
    echo Starting Frontend Development Server...
    start "AZOM Frontend" cmd /k "title AZOM Frontend && npm run dev"
    cd ../../../../..
) else (
    echo Frontend directory not found. Skipping frontend...
)

echo.
echo =======================================
echo   AZOM AI Agent is starting...
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
if exist "app\pipelineserver\pipeline_app\admin\frontend\" (
    echo   - Frontend: http://localhost:3000
)
echo.
echo Press any key to stop all services...
pause >nul

taskkill /F /FI "WINDOWTITLE eq AZOM Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq AZOM Frontend*" >nul 2>&1

exit /b 0
