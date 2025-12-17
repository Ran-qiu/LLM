#!/bin/bash

# LLM 管理平台 - 状态检查脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================"
echo "  LLM 管理平台 - 运行状态"
echo "========================================"
echo ""

# 检查后端
echo -e "${BLUE}后端服务:${NC}"
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "  状态: ${GREEN}运行中${NC}"
        echo "  PID: $BACKEND_PID"
        echo "  地址: http://localhost:8000"
        echo "  日志: logs/backend.log"
    else
        echo -e "  状态: ${RED}已停止${NC}"
    fi
else
    echo -e "  状态: ${YELLOW}未启动${NC}"
fi

echo ""

# 检查前端
echo -e "${BLUE}前端服务:${NC}"
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "  状态: ${GREEN}运行中${NC}"
        echo "  PID: $FRONTEND_PID"
        echo "  地址: http://localhost:5173"
        echo "  日志: logs/frontend.log"
    else
        echo -e "  状态: ${RED}已停止${NC}"
    fi
else
    echo -e "  状态: ${YELLOW}未启动${NC}"
fi

echo ""

# 检查端口
echo -e "${BLUE}端口占用:${NC}"
if command -v lsof &> /dev/null; then
    PORT_8000=$(lsof -i :8000 -t 2>/dev/null)
    PORT_5173=$(lsof -i :5173 -t 2>/dev/null)

    if [ -n "$PORT_8000" ]; then
        echo -e "  8000: ${GREEN}使用中${NC} (PID: $PORT_8000)"
    else
        echo -e "  8000: ${YELLOW}空闲${NC}"
    fi

    if [ -n "$PORT_5173" ]; then
        echo -e "  5173: ${GREEN}使用中${NC} (PID: $PORT_5173)"
    else
        echo -e "  5173: ${YELLOW}空闲${NC}"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -tuln | grep -q ":8000 "; then
        echo -e "  8000: ${GREEN}使用中${NC}"
    else
        echo -e "  8000: ${YELLOW}空闲${NC}"
    fi

    if netstat -tuln | grep -q ":5173 "; then
        echo -e "  5173: ${GREEN}使用中${NC}"
    else
        echo -e "  5173: ${YELLOW}空闲${NC}"
    fi
fi

echo ""
echo "========================================"
echo ""
