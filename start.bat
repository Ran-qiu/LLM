@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   LLM 管理平台 - 一键启动脚本
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "backend" (
    echo [错误] 请在项目根目录运行此脚本！
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo [1/5] 检查环境...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo 请先安装 Python 3.9+ : https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python 已安装

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js！
    echo 请先安装 Node.js 18+ : https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js 已安装
echo.

REM 检查并创建虚拟环境
echo [2/5] 准备后端环境...
cd backend

if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败！
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate

REM 检查依赖
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 首次运行，正在安装后端依赖...
    echo 这可能需要几分钟，请耐心等待...
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
    echo ✓ 后端依赖安装完成
) else (
    echo ✓ 后端依赖已安装
)
echo.

REM 检查并创建 .env
if not exist ".env" (
    echo 创建后端配置文件...
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo SECRET_KEY=dev-secret-key-change-in-production > .env
        echo ENCRYPTION_KEY=dev-encryption-key-change-in-production >> .env
        echo DATABASE_URL=sqlite:///./data/llm_manager.db >> .env
        echo ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000 >> .env
        echo LOG_LEVEL=INFO >> .env
    )
    echo ✓ 配置文件已创建
)

REM 检查数据库
if not exist "data\llm_manager.db" (
    echo [3/5] 初始化数据库...
    mkdir data 2>nul
    alembic upgrade head
    if errorlevel 1 (
        echo [警告] 数据库迁移失败，将在启动时自动创建
    ) else (
        echo ✓ 数据库初始化完成
    )
) else (
    echo [3/5] ✓ 数据库已存在
)
echo.

REM 启动后端
echo [4/5] 启动后端服务...
echo 后端将在 http://localhost:8000 运行
echo API 文档: http://localhost:8000/docs
echo.
start "LLM后端" cmd /k "cd /d %CD% && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM 等待后端启动
echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

cd ..

REM 检查前端依赖
echo [5/5] 准备前端环境...
cd frontend

if not exist "node_modules" (
    echo 首次运行，正在安装前端依赖...
    echo 这可能需要几分钟，请耐心等待...
    call npm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败！
        pause
        exit /b 1
    )
    echo ✓ 前端依赖安装完成
) else (
    echo ✓ 前端依赖已安装
)
echo.

REM 检查并创建前端 .env
if not exist ".env" (
    echo 创建前端配置文件...
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo VITE_API_BASE_URL=http://localhost:8000/api/v1 > .env
        echo VITE_APP_TITLE=LLM 管理平台 >> .env
    )
    echo ✓ 前端配置文件已创建
)

REM 启动前端
echo 启动前端服务...
echo 前端将在 http://localhost:5173 运行
echo.
start "LLM前端" cmd /k "cd /d %CD% && npm run dev"

REM 等待前端启动
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   🎉 启动完成！
echo ========================================
echo.
echo 📱 前端地址: http://localhost:5173
echo 📚 API文档:  http://localhost:8000/docs
echo.
echo 💡 提示:
echo   - 两个命令窗口会自动打开（后端和前端）
echo   - 关闭这些窗口即可停止服务
echo   - 下次启动只需双击此脚本即可
echo.
echo 按任意键打开浏览器...
pause >nul

REM 打开浏览器
start http://localhost:5173

echo.
echo 按任意键关闭此窗口...
pause >nul
