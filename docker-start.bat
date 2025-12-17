@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   LLM 管理平台 - Docker 一键启动
echo ========================================
echo.

REM 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker！
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo ✓ Docker 已安装
echo.

echo [1/3] 构建 Docker 镜像...
echo 这可能需要几分钟，请耐心等待...
docker compose build
if errorlevel 1 (
    echo [错误] 镜像构建失败！
    pause
    exit /b 1
)
echo ✓ 镜像构建完成
echo.

echo [2/3] 启动服务...
docker compose up -d
if errorlevel 1 (
    echo [错误] 服务启动失败！
    pause
    exit /b 1
)
echo ✓ 服务已启动
echo.

echo [3/3] 检查服务状态...
timeout /t 5 /nobreak >nul
docker compose ps
echo.

echo ========================================
echo   🎉 启动完成！
echo ========================================
echo.
echo 📱 前端地址: http://localhost:5173
echo 📚 API文档:  http://localhost:8000/docs
echo 📊 健康检查: http://localhost:8000/health
echo.
echo 💡 提示:
echo   - 查看日志: docker compose logs -f
echo   - 停止服务: docker compose stop
echo   - 重启服务: docker compose restart
echo   - 删除容器: docker compose down
echo.
echo 正在打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.
echo 按任意键关闭此窗口...
pause >nul
