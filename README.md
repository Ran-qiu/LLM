# LLM 统一管理平台

一个专注于本地化的大语言模型统一管理平台，支持 Ollama、OpenAI 兼容接口以及自定义网关。

## 核心功能

- **Ollama 深度集成**：完整支持本地部署的开源模型（Llama 3, Mistral, Qwen 等），支持流式对话。
- **本地 API 支持**：支持任何兼容 OpenAI API 格式的本地服务（如 vLLM, FastChat, LocalAI 等）。
- **自托管网关**：内置网关适配器模式，可作为统一入口管理多个下游模型服务。
- **多厂商支持**：除了本地模型，也支持 OpenAI, Claude, Gemini 等主流云端 API。
- **数据隐私**：对话记录和配置完全本地存储（SQLite），保护您的数据安全。
- **现代化界面**：React + TypeScript 构建的响应式 Web 界面。

## 技术栈

- **前端**: React 18 + TypeScript + Vite + Ant Design
- **后端**: Python 3.10+ + FastAPI + SQLAlchemy
- **LLM 引擎**: Ollama + OpenAI SDK (兼容协议)
- **数据库**: SQLite
- **部署**: Docker + Docker Compose

## 快速开始

### 方式一：Docker 一键部署（推荐）

最简单的运行方式，包含后端、前端和 Ollama 服务。

1. **准备环境**
   确保已安装 Docker 和 Docker Compose。

2. **启动服务**

   ```bash
   cd LLM
   docker-compose up -d
   ```

3. **访问应用**
   - **Web 界面**: <http://localhost:5173> (或 <http://localhost:80>)
   - **后端 API**: <http://localhost:8000>
   - **API 文档**: <http://localhost:8000/docs>
   - **Ollama**: <http://localhost:11434> (服务内置)

### 方式二：本地开发部署

如果您想在本地运行源码（Windows 环境示例）。

#### 1. 后端 (Backend)

```powershell
cd LLM/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端 (Frontend)

```powershell
cd LLM/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 3. Ollama (可选)

如果您没有使用 Docker 启动 Ollama，请确保您已在本地安装并运行了 Ollama：

- 下载安装: <https://ollama.com/>
- 启动服务: `ollama serve`
- 拉取模型: `ollama pull llama3`

## 功能指南

### 自托管网关 (Gateway)

平台支持 "Gateway" 模式，允许您连接到任何兼容 OpenAI 接口的服务。这对于使用 OneAPI、vLLM 或其他聚合网关非常有用。

**配置示例：**

- **Provider**: Gateway (或 Custom)
- **Base URL**: `http://localhost:8080/v1` (您的网关地址)
- **API Key**: `sk-xxxx` (您的网关密钥)
- **Model Type**: `openai-compatible`

### Ollama 集成

系统会自动检测配置的 Ollama 地址（默认为 `http://localhost:11434`）。

- 在设置中选择 "Ollama" 提供商。
- 系统会自动列出您已拉取的模型。

## 贡献

欢迎提交 Pull Request 或 Issue。

## 许可证

MIT License
