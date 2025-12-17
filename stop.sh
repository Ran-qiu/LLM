#!/bin/bash

# LLM 管理平台 - 停止脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "========================================"
echo "  停止 LLM 管理平台"
echo "========================================"
echo ""

# 停止后端
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo -e "${GREEN}✓ 后端已停止${NC}"
    else
        echo -e "${YELLOW}后端服务未运行${NC}"
    fi
    rm backend.pid
else
    echo -e "${YELLOW}未找到后端 PID 文件${NC}"
fi

# 停止前端
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ 前端已停止${NC}"
    else
        echo -e "${YELLOW}前端服务未运行${NC}"
    fi
    rm frontend.pid
else
    echo -e "${YELLOW}未找到前端 PID 文件${NC}"
fi

# 杀死所有相关进程（备用方案）
echo ""
echo "检查残留进程..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo -e "${GREEN}✓ 清理后端进程${NC}"
pkill -f "vite" 2>/dev/null && echo -e "${GREEN}✓ 清理前端进程${NC}"

echo ""
echo -e "${GREEN}所有服务已停止${NC}"
echo ""
