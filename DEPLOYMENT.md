# LLM 管理平台 - 部署文档

本文档提供了 LLM 管理平台的完整部署指南，包括本地部署和 Docker 部署两种方式。

---

## 📋 目录

- [系统要求](#系统要求)
- [方式一：本地部署](#方式一本地部署)
  - [1. 环境准备](#1-环境准备)
  - [2. 后端部署](#2-后端部署)
  - [3. 前端部署](#3-前端部署)
  - [4. 验证部署](#4-验证部署)
- [方式二：Docker 部署](#方式二docker-部署)
  - [1. Docker 环境准备](#1-docker-环境准备)
  - [2. 使用 Docker Compose](#2-使用-docker-compose)
  - [3. 验证部署](#3-验证部署)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [生产环境建议](#生产环境建议)

---

## 系统要求

### 最低配置

- **CPU**: 2 核心
- **内存**: 4GB RAM
- **硬盘**: 20GB 可用空间
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)

### 推荐配置

- **CPU**: 4 核心或更多
- **内存**: 8GB RAM 或更多
- **硬盘**: 50GB SSD
- **操作系统**: Ubuntu 22.04 LTS 或 Windows 11

---

## 方式一：本地部署

### 1. 环境准备

#### 1.1 安装 Python

**Windows:**

```bash
# 下载并安装 Python 3.9 或更高版本
# https://www.python.org/downloads/

# 验证安装
python --version  # 应显示 Python 3.9.x 或更高
pip --version
```

**Linux/macOS:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip

# macOS (使用 Homebrew)
brew install python@3.9

# 验证安装
python3 --version
pip3 --version
```

#### 1.2 安装 Node.js

**Windows:**

```bash
# 下载并安装 Node.js 18.x LTS
# https://nodejs.org/

# 验证安装
node --version  # 应显示 v18.x.x 或更高
npm --version
```

**Linux:**

```bash
# 使用 NodeSource 安装
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

**macOS:**

```bash
# 使用 Homebrew
brew install node@18

# 验证安装
node --version
npm --version
```

#### 1.3 克隆项目

```bash
# 克隆代码仓库
git clone https://github.com/Ran-qiu/LLM.git
cd LLM
```

---

### 2. 后端部署

#### 2.1 创建虚拟环境

**Windows:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖

```bash
# 确保虚拟环境已激活
pip install --upgrade pip
pip install -r requirements.txt
```

如果遇到依赖安装问题：

```bash
# Windows 可能需要
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Linux 可能需要额外的系统包
sudo apt-get install python3-dev build-essential
```

#### 2.3 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# Windows: notepad .env
# Linux/macOS: nano .env 或 vim .env
```

**必须配置的环境变量**：

```bash
# JWT 密钥 (必须修改为随机字符串)
SECRET_KEY=your-super-secret-key-change-this-in-production

# 数据库配置
DATABASE_URL=sqlite:///./data/llm_manager.db

# 加密密钥 (必须修改为随机字符串)
ENCRYPTION_KEY=your-encryption-key-change-this-in-production

# CORS 配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# 日志级别
LOG_LEVEL=INFO
```

**生成安全的密钥**：

```bash
# 使用 Python 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 复制输出到 SECRET_KEY

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# 复制输出到 ENCRYPTION_KEY
```

#### 2.4 初始化数据库

```bash
# 确保在 backend 目录下，虚拟环境已激活

# 创建数据目录
mkdir -p data

# 运行数据库迁移
alembic upgrade head
```

成功后会看到：

```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial_schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, add_phase5_features
```

#### 2.5 启动后端服务

**开发模式**：

```bash
# 确保在 backend 目录下
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**生产模式**：

```bash
# 使用 gunicorn (推荐)
pip install gunicorn

# 启动 4 个工作进程
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

验证后端是否启动成功：

```bash
# 打开浏览器访问
http://localhost:8000/docs
# 应该看到 FastAPI 的 Swagger 文档
```

---

### 3. 前端部署

#### 3.1 安装依赖

打开**新的终端窗口**：

```bash
cd frontend
npm install
```

如果遇到依赖安装问题：

```bash
# 清理缓存后重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 3.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# Windows: notepad .env
# Linux/macOS: nano .env
```

**.env 配置**：

```bash
# API 地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用标题
VITE_APP_TITLE=LLM 管理平台
```

#### 3.3 启动前端服务

**开发模式**：

```bash
# 确保在 frontend 目录下
npm run dev
```

成功后会看到：

```
  VITE v5.0.8  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**生产构建**：

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
# 可以使用任何静态服务器部署，例如：
npm install -g serve
serve -s dist -l 5173
```

---

### 4. 验证部署

#### 4.1 访问应用

打开浏览器访问：

- **前端**: <http://localhost:5173>
- **后端 API 文档**: <http://localhost:8000/docs>

#### 4.2 测试基本功能

1. **注册新用户**
   - 访问前端页面
   - 点击"立即注册"
   - 填写用户名、邮箱、密码
   - 提交注册

2. **登录**
   - 使用注册的账号登录
   - 应该自动跳转到聊天页面

3. **添加 API Key**
   - 导航到 "API Keys" 页面
   - 点击"添加 API Key"
   - 选择提供商并填写信息
   - 保存

4. **创建对话**
   - 返回"对话"页面
   - 点击"新建对话"
   - 选择 API Key 和模型
   - 创建对话并发送消息

#### 4.3 检查日志

**后端日志**：

```bash
# 查看实时日志
tail -f backend/logs/app.log

# 查看错误日志
tail -f backend/logs/error.log
```

**前端日志**：

- 打开浏览器开发者工具 (F12)
- 查看 Console 标签页

---

## 方式二：Docker 部署

### 1. Docker 环境准备

#### 1.1 安装 Docker

**Windows:**

```bash
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop/

# 验证安装
docker --version
docker-compose --version
```

**Linux (Ubuntu):**

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 安装 Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

**macOS:**

```bash
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop/

# 或使用 Homebrew
brew install --cask docker

# 验证安装
docker --version
docker compose version
```

#### 1.2 克隆项目

```bash
git clone https://github.com/Ran-qiu/LLM.git
cd LLM
```

---

### 2. 使用 Docker Compose

#### 2.1 创建 Docker Compose 配置

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: llm-backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY:-your-super-secret-key-change-in-production}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY:-your-encryption-key-change-in-production}
      - DATABASE_URL=sqlite:///./data/llm_manager.db
      - ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
      - LOG_LEVEL=INFO
    volumes:
      - ./backend/data:/app/data
      - ./backend/logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_BASE_URL=http://localhost:8000/api/v1
    container_name: llm-frontend
    ports:
      - "5173:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

networks:
  default:
    name: llm-network
```

#### 2.2 创建后端 Dockerfile

在 `backend/` 目录下创建 `Dockerfile`：

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据和日志目录
RUN mkdir -p data logs

# 暴露端口
EXPOSE 8000

# 健康检查端点
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动应用
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

#### 2.3 创建前端 Dockerfile

在 `frontend/` 目录下创建 `Dockerfile`：

```dockerfile
# frontend/Dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建参数
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### 2.4 创建 Nginx 配置

在 `frontend/` 目录下创建 `nginx.conf`：

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/json application/javascript;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # API 代理 (可选)
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2.5 创建环境变量文件

在项目根目录创建 `.env` 文件：

```bash
# .env
# JWT 密钥
SECRET_KEY=your-super-secret-key-please-change-this

# 加密密钥
ENCRYPTION_KEY=your-encryption-key-please-change-this

# 数据库
DATABASE_URL=sqlite:///./data/llm_manager.db

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# 日志
LOG_LEVEL=INFO
```

#### 2.6 构建并启动服务

```bash
# 在项目根目录执行

# 构建镜像
docker compose build

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 查看运行状态
docker compose ps
```

成功后会看到：

```
NAME                IMAGE                 STATUS              PORTS
llm-backend         llm-backend:latest    Up 30 seconds       0.0.0.0:8000->8000/tcp
llm-frontend        llm-frontend:latest   Up 30 seconds       0.0.0.0:5173->80/tcp
```

#### 2.7 停止和重启服务

```bash
# 停止服务
docker compose stop

# 重启服务
docker compose restart

# 停止并删除容器
docker compose down

# 停止并删除容器和数据卷
docker compose down -v
```

---

### 3. 验证部署

访问以下地址验证部署：

- **前端应用**: <http://localhost:5173>
- **后端 API 文档**: <http://localhost:8000/docs>
- **健康检查**: <http://localhost:8000/health>

---

## 配置说明

### 环境变量详解

#### 后端环境变量

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|---------|
| `SECRET_KEY` | JWT 密钥 | - | ✅ 必需 |
| `ENCRYPTION_KEY` | API Key 加密密钥 | - | ✅ 必需 |
| `DATABASE_URL` | 数据库连接 URL | `sqlite:///./data/llm_manager.db` | ✅ 必需 |
| `ALLOWED_ORIGINS` | 允许的跨域来源 | - | ✅ 必需 |
| `LOG_LEVEL` | 日志级别 | `INFO` | ❌ 可选 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间 | `30` | ❌ 可选 |

#### 前端环境变量

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|---------|
| `VITE_API_BASE_URL` | 后端 API 地址 | `http://localhost:8000/api/v1` | ✅ 必需 |
| `VITE_APP_TITLE` | 应用标题 | `LLM 管理平台` | ❌ 可选 |

### 数据库配置

#### SQLite (默认)

```bash
DATABASE_URL=sqlite:///./data/llm_manager.db
```

#### PostgreSQL (生产推荐)

```bash
# 安装 PostgreSQL 驱动
pip install psycopg2-binary

# 配置连接
DATABASE_URL=postgresql://username:password@localhost:5432/llm_manager
```

---

## 常见问题

### 1. 后端启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:

```bash
# 确保虚拟环境已激活
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# 重新安装依赖
pip install -r requirements.txt
```

---

### 2. 数据库迁移失败

**问题**: `alembic.util.exc.CommandError`

**解决**:

```bash
# 检查 alembic 配置
cat alembic.ini

# 确保数据目录存在
mkdir -p data

# 重新运行迁移
alembic upgrade head
```

---

### 3. 前端无法连接后端

**问题**: 前端请求返回 CORS 错误

**解决**:

1. 检查后端 `.env` 中的 `ALLOWED_ORIGINS`
2. 确保包含前端地址：`http://localhost:5173`
3. 重启后端服务

---

### 4. Docker 容器无法启动

**问题**: 容器启动后立即退出

**解决**:

```bash
# 查看详细日志
docker compose logs backend
docker compose logs frontend

# 检查端口是否被占用
# Windows
netstat -ano | findstr :8000
# Linux/macOS
lsof -i :8000

# 修改端口映射
# 编辑 docker-compose.yml
ports:
  - "8001:8000"  # 使用不同的端口
```

---

### 5. API Key 加密失败

**问题**: 添加 API Key 时报错

**解决**:

```bash
# 生成新的加密密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 更新 .env 文件
ENCRYPTION_KEY=生成的密钥

# 重启后端
```

---

### 6. 前端构建失败

**问题**: `npm run build` 失败

**解决**:

```bash
# 清理缓存
npm cache clean --force
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 检查 Node.js 版本
node --version  # 应该是 v18.x 或更高

# 如果版本太低，升级 Node.js
```

---

## 生产环境建议

### 1. 数据库

**不要在生产环境使用 SQLite**，推荐使用 PostgreSQL：

```bash
# Docker Compose 添加 PostgreSQL
services:
  postgres:
    image: postgres:15-alpine
    container_name: llm-postgres
    environment:
      POSTGRES_DB: llm_manager
      POSTGRES_USER: llm_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  backend:
    # ... 其他配置
    environment:
      - DATABASE_URL=postgresql://llm_user:secure_password@postgres:5432/llm_manager
    depends_on:
      - postgres

volumes:
  postgres_data:
```

### 2. 反向代理

使用 Nginx 作为反向代理：

```nginx
# /etc/nginx/sites-available/llm-manager
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. HTTPS 配置

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 4. 系统服务

创建 systemd 服务文件：

```ini
# /etc/systemd/system/llm-backend.service
[Unit]
Description=LLM Manager Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/llm/backend
Environment="PATH=/var/www/llm/backend/venv/bin"
ExecStart=/var/www/llm/backend/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable llm-backend
sudo systemctl start llm-backend
sudo systemctl status llm-backend
```

### 5. 监控和日志

**日志管理**:

```bash
# 使用 logrotate
sudo nano /etc/logrotate.d/llm-manager

/var/www/llm/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload llm-backend > /dev/null 2>&1 || true
    endscript
}
```

**性能监控**:

```bash
# 安装监控工具
pip install prometheus-fastapi-instrumentator

# 在 app/main.py 中添加
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 6. 备份策略

**数据库备份**:

```bash
# PostgreSQL 备份脚本
#!/bin/bash
# /usr/local/bin/backup-llm-db.sh

BACKUP_DIR="/var/backups/llm"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="llm_manager_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -U llm_user llm_manager > $BACKUP_DIR/$FILENAME
gzip $BACKUP_DIR/$FILENAME

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

**定时任务**:

```bash
# 添加到 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /usr/local/bin/backup-llm-db.sh
```

### 7. 安全加固

```bash
# 1. 防火墙配置
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 2. 限制文件权限
chmod 600 backend/.env
chmod 700 backend/data

# 3. 禁用 debug 模式
# 确保 .env 中
LOG_LEVEL=WARNING

# 4. 使用强密码
# 定期更新 SECRET_KEY 和 ENCRYPTION_KEY
```

---

## 🎉 部署完成

恭喜！您已成功部署 LLM 管理平台。

**快速链接**:

- 📱 前端应用: <http://localhost:5173>
- 📚 API 文档: <http://localhost:8000/docs>
- 📊 健康检查: <http://localhost:8000/health>

**下一步**:

1. 创建管理员账号
2. 添加 LLM API Keys
3. 开始使用聊天功能
4. 查看使用统计

**需要帮助？**

- 查看 [QUICKSTART.md](./QUICKSTART.md) 了解快速开始
- 查看 [开发文档.md](./开发文档.md) 了解更多功能
- 访问 [GitHub Issues](https://github.com/Ran-qiu/LLM/issues) 报告问题

---

**文档版本**: 1.0
**更新日期**: 2025-12-17
**维护者**: LLM Manager Team
