#!/bin/bash

# LLM 管理平台 - Docker 一键启动脚本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================"
echo "  LLM 管理平台 - Docker 一键启动"
echo "========================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 Docker！${NC}"
    echo "请先安装 Docker"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装${NC}"
echo ""

echo -e "${BLUE}[1/3] 构建 Docker 镜像...${NC}"
echo "这可能需要几分钟，请耐心等待..."
docker compose build
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 镜像构建失败！${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

echo -e "${BLUE}[2/3] 启动服务...${NC}"
docker compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 服务启动失败！${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 服务已启动${NC}"
echo ""

echo -e "${BLUE}[3/3] 检查服务状态...${NC}"
sleep 5
docker compose ps
echo ""

echo "========================================"
echo -e "  ${GREEN}🎉 启动完成！${NC}"
echo "========================================"
echo ""
echo -e "📱 前端地址: ${BLUE}http://localhost:5173${NC}"
echo -e "📚 API文档:  ${BLUE}http://localhost:8000/docs${NC}"
echo -e "📊 健康检查: ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo "💡 提示:"
echo "  - 查看日志: docker compose logs -f"
echo "  - 停止服务: docker compose stop"
echo "  - 重启服务: docker compose restart"
echo "  - 删除容器: docker compose down"
echo ""

# 尝试打开浏览器
if command -v xdg-open &> /dev/null; then
    sleep 3
    xdg-open http://localhost:5173 &> /dev/null &
elif command -v open &> /dev/null; then
    sleep 3
    open http://localhost:5173 &> /dev/null &
fi

echo "服务已在后台运行"
