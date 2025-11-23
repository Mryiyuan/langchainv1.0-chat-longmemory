# 🤖 LangChain 聊天系统 - 长期记忆

基于 LangChain、LangGraph 和 Milvus 的智能对话系统，具有长期记忆功能，能够跨对话记住用户信息。

## ✨ 功能特点

- 🧠 **长期记忆**：使用 Milvus 向量数据库存储重要信息，跨对话记忆用户偏好
- 💬 **多线程对话**：支持同时管理多个对话线程
- 🔄 **流式输出**：实时显示 AI 回复，提升用户体验
- 📊 **对话统计**：提供详细的对话历史和统计信息
- 🗄️ **持久化存储**：使用 SQLite 存储对话历史
- 🎯 **智能记忆提取**：自动识别并保存重要用户信息

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面      │    │   LangGraph     │    │   Milvus        │
│                 │    │                 │    │                 │
│ • 多线程管理    │◄──►│ • 对话流程控制  │◄──►│ • 长期记忆存储  │
│ • 历史查看      │    │ • 状态管理      │    │ • 语义检索      │
│ • 统计信息      │    │ • MemorySaver   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SQLite        │
                    │                 │
                    │ • 对话历史      │
                    │ • 消息存储      │
                    │ • 持久化        │
                    └─────────────────┘
```
记忆系统三层：

1️⃣ 短期记忆（当前会话）
   └─ MemorySaver（内存）
   └─ 用途：LLM 当前对话上下文
   └─ 范围：程序运行期间

2️⃣ 中期记忆（对话历史）
   └─ SQLite（本地数据库）
   └─ 用途：重启后恢复对话
   └─ 范围：每个 thread_id 的完整历史

3️⃣ 长期记忆（跨线程知识库）
   └─ Milvus（向量数据库）
   └─ 用途：任何线程都能查到用户信息
   └─ 范围：全局用户档案
## 🚀 快速开始

### 环境要求

- Python 3.8+
- CUDA 支持的 GPU (推荐，用于加速 embeddings)
- Milvus 数据库服务

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置设置

1. 复制并编辑配置文件：
```bash
cp config/config.py.example config/config.py
```

2. 修改 `config/config.py` 中的配置：
   - DeepSeek API 密钥
   - Milvus 连接信息
   - 模型路径设置

### 运行系统

```bash
python main.py
```

## 📖 使用指南

### 基本操作

1. **新建对话**：创建新的对话线程
2. **继续对话**：在已有对话中继续交流
3. **查看对话总结**：查看对话历史和长期记忆
4. **查看历史对话**：浏览完整的对话记录
5. **删除对话**：删除不需要的对话线程

### 长期记忆功能

系统会自动识别并保存以下类型的信息：
- 个人基本信息（姓名、职业等）
- 兴趣爱好
- 重要经历
- 偏好设置

这些信息将在后续对话中被自动检索，提供更加个性化的回复。

## 🔧 技术栈

- **LangChain**: LLM 应用开发框架
- **LangGraph**: 对话状态管理
- **Milvus**: 向量数据库，用于长期记忆存储
- **SQLite**: 轻量级关系数据库，存储对话历史
- **Sentence-Transformers**: 本地文本嵌入模型
- **DeepSeek**: 大语言模型 API

## 📁 项目结构

```
langchain_chat_longMemory/
├── main.py                    # 主程序入口
├── conversation_system_new.py  # 对话系统核心逻辑
├── embeddings_model.py        # 文本嵌入模型
├── config/
│   └── config.py             # 配置文件
├── conversations.db          # SQLite 数据库（运行时生成）
├── saved_threads.json        # 对话线程信息（运行时生成）
└── requirements.txt          # 依赖列表
```

## ⚙️ 配置说明

### 模型配置

```python
# DeepSeek API 配置
deepseek_API_KEY: str = "your-api-key"
deepseek_BASE_URL: str = "https://api.deepseek.com"
deepseek_MODEL_NAME: str = "deepseek-chat"
deepseek_REASONER_MODEL_NAME: str = "deepseek-reasoner"

# 嵌入模型配置
EMBEDDINGS_MODEL_NAME: str = "/model/all-MiniLM-L6-v2"
```

### 数据库配置

```python
# Milvus 配置
MILVUS_URI = "http://localhost:19530"
MILVUS_DATABASE = "rag_db"
MILVUS_COLLECTION_NAME = "user_memories"
```

## 🔍 故障排除

### 常见问题

1. **嵌入模型加载失败**
   - 检查模型路径是否正确
   - 确保有足够的磁盘空间存储模型

2. **Milvus 连接失败**
   - 确认 Milvus 服务正在运行
   - 检查网络连接和防火墙设置

3. **API 调用失败**
   - 验证 API 密钥是否有效
   - 检查网络连接和 API 端点

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 应用开发框架
- [Milvus](https://github.com/milvus-io/milvus) - 高性能向量数据库
- [Sentence-Transformers](https://github.com/UKPLab/sentence-transformers) - 优秀的文本嵌入模型库