@echo off
echo.
echo ========================================
echo   LLM Manager - Quick Start
echo ========================================
echo.

REM Check if in project root
if not exist "backend" (
    echo [ERROR] Please run this script in project root directory!
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Save root directory
set ROOT_DIR=%CD%

echo [1/5] Checking environment...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.9+: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python installed

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js installed
echo.

REM Setup backend
echo [2/5] Setting up backend...
cd backend

REM Save backend directory path
set BACKEND_DIR=%CD%

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate venv
call venv\Scripts\activate

REM Check dependencies
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing backend dependencies (this may take a few minutes)...
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [OK] Backend dependencies installed
) else (
    echo [OK] Backend dependencies already installed
)
echo.

REM Create .env if not exists
if not exist ".env" (
    echo Creating backend config file...
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo SECRET_KEY=dev-secret-key-change-in-production > .env
        echo ENCRYPTION_KEY=dev-encryption-key-change-in-production >> .env
        echo DATABASE_URL=sqlite:///./data/llm_manager.db >> .env
        echo ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000 >> .env
        echo LOG_LEVEL=INFO >> .env
    )
    echo [OK] Config file created
)

REM Initialize database
if not exist "data\llm_manager.db" (
    echo [3/5] Initializing database...
    mkdir data 2>nul
    alembic upgrade head
    if errorlevel 1 (
        echo [WARNING] Database migration failed, will be created on startup
    ) else (
        echo [OK] Database initialized
    )
) else (
    echo [3/5] [OK] Database already exists
)
echo.

REM Start backend
echo [4/5] Starting backend service...
echo Backend will run at http://localhost:8000
echo API docs at http://localhost:8000/docs
echo.
start "LLM-Backend" cmd /k "cd /d "%BACKEND_DIR%" && call venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

cd "%ROOT_DIR%"

REM Setup frontend
echo [5/5] Setting up frontend...
cd frontend

REM Save frontend directory path
set FRONTEND_DIR=%CD%

if not exist "node_modules" (
    echo Installing frontend dependencies (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        pause
        exit /b 1
    )
    echo [OK] Frontend dependencies installed
) else (
    echo [OK] Frontend dependencies already installed
)
echo.

REM Create frontend .env
if not exist ".env" (
    echo Creating frontend config file...
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo VITE_API_BASE_URL=http://localhost:8000/api/v1 > .env
        echo VITE_APP_TITLE=LLM Manager >> .env
    )
    echo [OK] Frontend config created
)

REM Start frontend
echo Starting frontend service...
echo Frontend will run at http://localhost:5173
echo.
start "LLM-Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

REM Wait for frontend
timeout /t 3 /nobreak >nul

cd "%ROOT_DIR%"

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Tips:
echo   - Two command windows will open (backend and frontend)
echo   - Close those windows to stop the services
echo   - Next time just double-click this script
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul

REM Open browser
start http://localhost:5173

echo.
echo Press any key to close this window...
pause >nul
