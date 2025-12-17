# 🚀 一键启动指南

本项目提供多种傻瓜式启动方案，选择最适合您的方式！

---

## 方式 1: Docker 一键启动 ⭐ **推荐**

**最简单的方式，无需配置环境！**

### Windows 用户
```bash
# 双击运行
docker-start.bat

# 或在命令行执行
.\docker-start.bat
```

### Linux/macOS 用户
```bash
# 添加执行权限
chmod +x docker-start.sh

# 运行
./docker-start.sh
```

### 优点
- ✅ 无需安装 Python 和 Node.js
- ✅ 环境完全隔离
- ✅ 一键启动和停止
- ✅ 生产环境推荐

### 前提条件
- 已安装 Docker Desktop

---

## 方式 2: 本地一键启动

**适合开发和调试**

### Windows 用户
```bash
# 双击运行
start.bat

# 或在命令行执行
.\start.bat
```

### Linux/macOS 用户
```bash
# 添加执行权限
chmod +x start.sh

# 运行
./start.sh
```

### 优点
- ✅ 代码修改实时生效
- ✅ 方便调试
- ✅ 性能更好

### 前提条件
- Python 3.9+
- Node.js 18+

---

## 管理命令 (Linux/macOS)

### 停止服务
```bash
./stop.sh
```

### 查看状态
```bash
./status.sh
```

### 查看日志
```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log
```

---

## Docker 管理命令

### 停止服务
```bash
docker compose stop
```

### 重启服务
```bash
docker compose restart
```

### 查看日志
```bash
# 实时日志
docker compose logs -f

# 查看后端日志
docker compose logs -f backend

# 查看前端日志
docker compose logs -f frontend
```

### 完全删除
```bash
# 删除容器和数据
docker compose down -v
```

---

## 访问地址

启动成功后，访问以下地址：

- 🌐 **前端应用**: http://localhost:5173
- 📚 **API 文档**: http://localhost:8000/docs
- 💚 **健康检查**: http://localhost:8000/health

---

## 首次使用

### 1. 注册账号
- 访问 http://localhost:5173
- 点击"立即注册"
- 填写用户名、邮箱、密码

### 2. 添加 API Key
- 登录后进入"API Keys"页面
- 点击"添加 API Key"
- 选择提供商（OpenAI、Claude等）
- 填写 API Key

### 3. 开始对话
- 进入"对话"页面
- 点击"新建对话"
- 选择 API Key 和模型
- 开始聊天！

---

## 常见问题

### 1. 端口被占用
如果 8000 或 5173 端口被占用：

**Windows:**
```bash
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 结束进程
taskkill /PID <进程ID> /F
```

**Linux/macOS:**
```bash
# 查看端口占用
lsof -i :8000
lsof -i :5173

# 结束进程
kill -9 <PID>
```

### 2. Docker 启动失败
```bash
# 清理并重新构建
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### 3. 虚拟环境问题 (本地启动)
```bash
# Windows
cd backend
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/macOS
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 性能优化

### 开发模式
- 自动重载
- 详细日志
- 适合调试

### 生产模式
```bash
# 使用 Gunicorn
cd backend
source venv/bin/activate
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

---

## 进阶选项

### 启动完整版本（包含 n8n 和 Ollama）
```bash
# Docker
docker compose --profile full up -d

# 访问 n8n: http://localhost:5678
# 访问 Ollama: http://localhost:11434
```

### 仅启动核心服务
```bash
# 默认只启动 backend 和 frontend
docker compose up -d
```

---

## 技术支持

遇到问题？

1. 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 完整部署文档
2. 查看 [QUICKSTART.md](./QUICKSTART.md) 快速开始指南
3. 提交 Issue: https://github.com/Ran-qiu/LLM/issues

---

**祝使用愉快！ 🎉**
