# LLM 统一管理平台

一个本地部署的大语言模型统一管理平台，支持多个主流LLM厂商的API调用，提供完整的对话管理和历史记录功能。

## 项目特点

- **多厂商支持**：统一接口调用 OpenAI、Claude、Gemini、通义千问等11+主流大模型
- **Ollama集成**：完整支持本地部署的开源模型（Llama 3、Mistral、Qwen等）
- **LangChain增强**：利用LangChain强大能力，支持对话记忆、工具调用、Agent等高级功能
- **自定义模型**：支持任何兼容OpenAI API格式的模型服务（OneAPI、vLLM、FastChat等）
- **n8n工作流**：集成n8n实现LLM自动化编排、定时任务、Webhook触发等场景
- **本地部署**：数据完全本地存储，保护隐私安全
- **用户友好**：现代化的Web界面，流畅的对话体验
- **完整功能**：用户认证、对话管理、历史记录、灵活的API密钥管理
- **易于部署**：Docker一键部署，开箱即用

## 技术栈

- **前端**: React 18 + TypeScript + Vite + Ant Design
- **后端**: Python 3.10+ + FastAPI + SQLAlchemy
- **LLM集成**: LangChain + Ollama + 原生SDK（OpenAI、Anthropic等）
- **工作流引擎**: n8n（自动化编排）
- **数据库**: SQLite
- **部署**: Docker + Docker Compose

## 支持的LLM厂商

### 云端API厂商

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- Google (Gemini Pro, Gemini Ultra)
- 阿里云通义千问
- 百度文心一言
- 智谱AI (ChatGLM)
- 讯飞星火
- 月之暗面 (Moonshot/Kimi)
- 腾讯混元
- DeepSeek

### 本地部署

- **Ollama**: 支持 Llama 3、Mistral、Qwen、CodeLlama、Phi 等多种开源模型

### 自定义服务

- 任何兼容 OpenAI API 格式的服务
- OneAPI 多模型聚合网关
- vLLM 高性能推理引擎
- FastChat 模型服务
- Text Generation Inference
- LocalAI

## 快速开始

### 使用Docker（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd LLM

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，设置必要的配置

# 启动服务（包含所有组件）
docker-compose up -d

# 访问应用
# 前端: http://localhost:80
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
# n8n工作流: http://localhost:5678 (默认用户名: admin, 密码: changeme123)
# Ollama API: http://localhost:11434 (如果启用)
```

### 本地开发

#### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 项目文档

详细的开发文档请查看：[开发文档.md](./开发文档.md)

文档包含：

- 完整的系统架构设计（包含 n8n 工作流引擎）
- 功能模块详细说明
- 数据库设计（支持自定义模型配置）
- API接口文档
- **Ollama 集成指南**（安装、配置、使用）
- **LangChain 集成指南**（对话记忆、工具调用、Agent）
- **自定义模型集成指南**（OneAPI、vLLM等）
- **n8n 工作流自动化指南**（定时任务、Webhook、批处理、工作流模板）
- 分阶段开发计划
- 部署指南
- 安全性考虑

## 项目状态

当前状态：**开发中**

- [x] 项目初始化
- [x] 开发文档编写
- [ ] 基础框架搭建
- [ ] 用户认证系统
- [ ] LLM适配器实现
- [ ] 对话功能实现
- [ ] 历史记录功能
- [ ] Docker化部署

## 贡献指南

欢迎贡献代码、报告问题或提出建议。请确保：

- 遵循项目的代码规范
- 编写必要的测试
- 提交前运行测试确保通过

## 许可证

[待定]

## 联系方式

如有问题或建议，请提交 Issue。
