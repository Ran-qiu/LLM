#!/bin/bash

# LLM 管理平台 - 一键启动脚本 (Linux/macOS)

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  LLM 管理平台 - 一键启动脚本"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ]; then
    echo -e "${RED}[错误] 请在项目根目录运行此脚本！${NC}"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo -e "${BLUE}[1/5] 检查环境...${NC}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 Python3！${NC}"
    echo "请先安装 Python 3.9+"
    exit 1
fi
echo -e "${GREEN}✓ Python 已安装${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 Node.js！${NC}"
    echo "请先安装 Node.js 18+"
    exit 1
fi
echo -e "${GREEN}✓ Node.js 已安装${NC}"
echo ""

# 准备后端
echo -e "${BLUE}[2/5] 准备后端环境...${NC}"
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
if ! pip show fastapi &> /dev/null; then
    echo "首次运行，正在安装后端依赖..."
    echo "这可能需要几分钟，请耐心等待..."
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 后端依赖已安装${NC}"
fi
echo ""

# 创建配置文件
if [ ! -f ".env" ]; then
    echo "创建后端配置文件..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=dev-encryption-key-change-in-production
DATABASE_URL=sqlite:///./data/llm_manager.db
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
EOF
    fi
    echo -e "${GREEN}✓ 配置文件已创建${NC}"
fi

# 初始化数据库
if [ ! -f "data/llm_manager.db" ]; then
    echo -e "${BLUE}[3/5] 初始化数据库...${NC}"
    mkdir -p data
    alembic upgrade head || echo -e "${YELLOW}[警告] 数据库迁移失败，将在启动时自动创建${NC}"
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
else
    echo -e "${BLUE}[3/5] ${GREEN}✓ 数据库已存在${NC}"
fi
echo ""

# 启动后端（后台运行）
echo -e "${BLUE}[4/5] 启动后端服务...${NC}"
echo "后端将在 http://localhost:8000 运行"
echo "API 文档: http://localhost:8000/docs"
echo ""

# 使用 nohup 在后台运行
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo -e "${GREEN}✓ 后端已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
echo "等待后端服务启动..."
sleep 5

cd ..

# 准备前端
echo -e "${BLUE}[5/5] 准备前端环境...${NC}"
cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "首次运行，正在安装前端依赖..."
    echo "这可能需要几分钟，请耐心等待..."
    npm install
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 前端依赖已安装${NC}"
fi
echo ""

# 创建配置文件
if [ ! -f ".env" ]; then
    echo "创建前端配置文件..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=LLM 管理平台
EOF
    fi
    echo -e "${GREEN}✓ 前端配置文件已创建${NC}"
fi

# 启动前端（后台运行）
echo "启动前端服务..."
echo "前端将在 http://localhost:5173 运行"
echo ""

nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✓ 前端已启动 (PID: $FRONTEND_PID)${NC}"

cd ..

echo ""
echo "========================================"
echo -e "  ${GREEN}🎉 启动完成！${NC}"
echo "========================================"
echo ""
echo -e "📱 前端地址: ${BLUE}http://localhost:5173${NC}"
echo -e "📚 API文档:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "💡 提示:"
echo "  - 日志文件: logs/backend.log 和 logs/frontend.log"
echo "  - 停止服务: ./stop.sh"
echo "  - 查看状态: ./status.sh"
echo ""
echo -e "${YELLOW}按 Ctrl+C 不会停止服务，请使用 ./stop.sh 停止${NC}"
echo ""

# 尝试打开浏览器（Linux）
if command -v xdg-open &> /dev/null; then
    sleep 3
    xdg-open http://localhost:5173 &> /dev/null &
elif command -v open &> /dev/null; then
    # macOS
    sleep 3
    open http://localhost:5173 &> /dev/null &
fi

echo "服务已在后台运行"
