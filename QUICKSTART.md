# LLM 管理平台 - 快速开始指南

## 📋 项目概述

统一大模型管理平台，支持多个 LLM 提供商（OpenAI、Claude、Gemini、Ollama 等），提供完整的对话管理、使用统计、分享、模板等功能。

### 技术栈
- **后端**: FastAPI + Python 3.9+
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **前端**: React + TypeScript + Vite + Ant Design
- **认证**: JWT
- **LLM 集成**: LangChain

---

## 🚀 快速开始

### 1. 后端设置

#### 安装依赖
```bash
cd backend
conda activate work  # 或使用你的 Python 环境
pip install -r requirements.txt
```

#### 配置环境变量
创建 `backend/.env` 文件：
```env
# 应用配置
PROJECT_NAME="LLM Manager"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# 数据库
DATABASE_URL="sqlite:///./llm_manager.db"

# 安全
SECRET_KEY="your-secret-key-here-change-in-production"
ENCRYPTION_KEY="your-encryption-key-32-chars-long!!"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

#### 初始化数据库
```bash
cd backend

# 应用所有迁移
alembic upgrade head

# 或者逐个应用
alembic upgrade 001  # 基础表
alembic upgrade 002  # Phase 5 功能
```

#### 启动后端服务
```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 2. 前端设置

#### 安装依赖
```bash
cd frontend
npm install
```

#### 配置代理
`frontend/vite.config.ts` 已配置代理到后端 API：
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

#### 启动前端
```bash
npm run dev
```

访问前端：http://localhost:5173

---

## 🗄️ 数据库管理

### 查看当前迁移状态
```bash
alembic current
```

### 查看迁移历史
```bash
alembic history
```

### 创建新迁移
```bash
# 自动检测模型变化
alembic revision --autogenerate -m "描述变更内容"

# 手动创建空迁移
alembic revision -m "描述变更内容"
```

### 回滚迁移
```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade 001
```

---

## 📝 API 使用示例

### 1. 用户注册
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123!"
```

返回：
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. 添加 API Key
```bash
curl -X POST "http://localhost:8000/api/v1/models/api-keys" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "name": "My OpenAI Key",
    "api_key": "sk-..."
  }'
```

### 4. 创建对话
```bash
curl -X POST "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试对话",
    "model": "gpt-4",
    "api_key_id": 1,
    "system_prompt": "你是一个有帮助的AI助手"
  }'
```

### 5. 发送消息
```bash
curl -X POST "http://localhost:8000/api/v1/chat/conversations/1/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好！"
  }'
```

---

## 🎯 核心功能说明

### Phase 1-4: 基础功能
✅ 用户认证和管理
✅ API Key 管理（支持 5+ 提供商）
✅ 对话管理和聊天功能
✅ 流式响应
✅ Token 使用追踪和成本计算

### Phase 5: 高级功能

#### 5.1 搜索和导出
- `GET /api/v1/chat/search` - 消息全文搜索
- `GET /api/v1/chat/conversations/{id}/export` - 导出对话（JSON/Markdown）

#### 5.2 使用统计
- `GET /api/v1/statistics/me` - 用户统计
- `GET /api/v1/statistics/conversations/{id}` - 对话统计

#### 5.3 标签和分享
- `GET/POST /api/v1/tags` - 管理标签
- `POST /api/v1/tags/{tag_id}/conversations/{conv_id}` - 标签分配
- `POST /api/v1/shares/conversations/{id}/share` - 创建分享链接
- `POST /api/v1/shares/{token}/access` - 访问分享（公开）

#### 5.4 编辑和模板
- `PUT /api/v1/chat/messages/{id}` - 编辑消息
- `DELETE /api/v1/chat/messages/{id}` - 删除消息
- `POST /api/v1/chat/messages/{id}/regenerate` - 重新生成响应
- `GET/POST /api/v1/templates` - 管理模板
- `POST /api/v1/templates/{id}/use` - 使用模板创建对话

#### 5.5 性能优化
- 数据库索引优化
- 内存缓存机制（支持 Redis）
- 查询性能监控

---

## 🔧 配置说明

### 支持的 LLM 提供商

| 提供商 | 配置示例 |
|--------|----------|
| OpenAI | `provider: "openai"`, `api_key: "sk-..."` |
| Claude | `provider: "claude"`, `api_key: "sk-ant-..."` |
| Gemini | `provider: "gemini"`, `api_key: "AI..."` |
| Ollama | `provider: "ollama"`, `base_url: "http://localhost:11434"` |
| Custom | `provider: "custom"`, 自定义配置 |

### 缓存配置

开发环境使用内存缓存（默认）：
```python
from app.core.caching import cache, cached

@cached(ttl=300, key_prefix="user")
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

生产环境推荐使用 Redis：
```bash
pip install redis
```

更新 `app/core/caching.py` 使用 RedisCache。

---

## 📊 数据库架构

### 核心表
- `users` - 用户
- `api_keys` - API 密钥（加密存储）
- `conversations` - 对话
- `messages` - 消息

### Phase 5 新增表
- `tags` - 标签
- `conversation_tags` - 对话-标签关联
- `shares` - 分享链接
- `templates` - 对话模板

### 性能索引
- `idx_conversations_user_updated` - 用户对话查询
- `idx_messages_conv_created` - 消息时间序列
- `idx_tags_user_name` - 标签查询
- `idx_shares_user_created` - 分享查询
- `idx_templates_user_updated` - 模板查询

---

## 🐳 Docker 部署

### 构建镜像
```bash
docker-compose build
```

### 启动服务
```bash
docker-compose up -d
```

### 查看日志
```bash
docker-compose logs -f backend
```

---

## 🧪 测试

### 运行测试
```bash
cd backend
pytest
```

### 测试覆盖率
```bash
pytest --cov=app --cov-report=html
```

---

## 📚 开发指南

### 添加新的 LLM 提供商

1. 在 `app/adapters/` 创建新的适配器
2. 继承 `BaseLLMAdapter`
3. 实现 `chat()` 和 `chat_stream()` 方法
4. 在 `LLMService` 中注册适配器

### 添加新的 API 端点

1. 在 `app/api/endpoints/` 创建路由文件
2. 在 `app/services/` 创建服务层
3. 在 `app/api/api.py` 注册路由

---

## 🔐 安全注意事项

1. **生产环境必须修改**：
   - `SECRET_KEY` - JWT 签名密钥
   - `ENCRYPTION_KEY` - API Key 加密密钥

2. **API Key 安全**：
   - 所有 API Key 使用 Fernet 加密存储
   - 永远不要在日志中输出明文 API Key

3. **CORS 配置**：
   - 生产环境限制 `BACKEND_CORS_ORIGINS` 为实际域名

4. **密码安全**：
   - 使用 bcrypt 哈希
   - 强制密码复杂度要求

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 支持

如有问题，请创建 GitHub Issue。
