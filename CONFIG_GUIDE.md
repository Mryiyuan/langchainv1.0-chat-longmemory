# 配置修改指南

## 概述

项目配置现在通过环境变量管理，而不是直接修改代码。这样做的好处是：
- 保护敏感信息（如 API 密钥）不被提交到版本控制系统
- 允许在不同环境中使用不同的配置
- 便于部署和配置管理

## 配置文件说明

### 1. config/config.py
这是配置文件的主文件，它从环境变量中读取配置值。你**不应该**直接修改这个文件，除非你需要添加新的配置项。

### 2. .env.example
这是环境变量的模板文件，展示了所有可配置的选项。这个文件会被提交到 Git，作为其他开发者的参考。

### 3. .env
这是实际的环境变量文件，包含你的个人配置。这个文件**不会**被提交到 Git（已在 .gitignore 中排除）。

## 如何修改配置

### 步骤 1：创建本地 .env 文件

如果你还没有 .env 文件，请先复制模板：
```bash
cp .env.example .env
```

### 步骤 2：编辑 .env 文件

使用你喜欢的编辑器打开 .env 文件：
```bash
nano .env
# 或者
vim .env
```

### 步骤 3：修改配置项

根据你的需求修改以下配置：

#### OpenAI API 配置
```bash
# 模型名称
MODEL_NAME=Qwen3-0.6B-GPTQ-Int8

# API 密钥（必须修改）
API_KEY=sk-你的实际API密钥

# API 基础 URL
BASE_URL=http://host.docker.internal:8800/v1

# 温度参数（控制输出的随机性）
TEMPERATURE=0
```

#### DeepSeek API 配置
```bash
# DeepSeek API 密钥（如果使用 DeepSeek 模型）
DEEPSEEK_API_KEY=sk-你的DeepSeek API密钥

# DeepSeek API 基础 URL
DEEPSEEK_BASE_URL=https://api.deepseek.com

# DeepSeek 模型名称
DEEPSEEK_MODEL_NAME=deepseek-chat

# DeepSeek 推理模型名称
DEEPSEEK_REASONER_MODEL_NAME=deepseek-reasoner
```

#### 嵌入模型配置
```bash
# 嵌入模型路径
EMBEDDINGS_MODEL_NAME=/model/all-MiniLM-L6-v2
```

#### 检索配置
```bash
# 检索时返回的最大相关文档数
TOP_K_RETRIEVAL=3

# 短期记忆保留的最大消息数
MAX_SHORT_TERM_MESSAGES=6
```

#### Milvus 数据库配置
```bash
# Milvus 服务器 URI
MILVUS_URI=http://192.168.50.3:19530

# Milvus 认证令牌
MILVUS_TOKEN=root:Milvus

# Milvus 数据库名称
MILVUS_DATABASE=rag_db

# Milvus 集合名称
MILVUS_COLLECTION_NAME=pharma_database

# Milvus 连接超时时间（秒）
MILVUS_TIMEOUT=10
```

## 常见配置场景

### 场景 1：使用 OpenAI API
```bash
MODEL_NAME=gpt-3.5-turbo
API_KEY=sk-你的OpenAI API密钥
BASE_URL=https://api.openai.com/v1
TEMPERATURE=0.7
```

### 场景 2：使用本地部署的模型
```bash
MODEL_NAME=your-local-model-name
API_KEY=sk-123456  # 本地模型可能需要虚拟密钥
BASE_URL=http://localhost:8000/v1
TEMPERATURE=0
```

### 场景 3：使用不同的 Milvus 实例
```bash
MILVUS_URI=http://your-milvus-server:19530
MILVUS_TOKEN=your-token
MILVUS_DATABASE=your-database
MILVUS_COLLECTION_NAME=your-collection
```

## 配置验证

修改配置后，你可以通过运行以下命令来验证配置是否正确加载：

```python
from config.config import config, milvus_config

print(f"Model Name: {config.MODEL_NAME}")
print(f"API Key: {config.API_KEY}")
print(f"Milvus URI: {milvus_config.MILVUS_URI}")
```

## 注意事项

1. **永远不要**将 .env 文件提交到版本控制系统
2. 确保 .env 文件中的敏感信息（如 API 密钥）是正确的
3. 在生产环境中，考虑使用更安全的环境变量管理方式
4. 如果你添加了新的配置项，请同时更新 .env.example 文件

## 故障排除

### 问题 1：配置未生效
- 确保 .env 文件在项目根目录
- 检查环境变量名称是否正确（大小写敏感）
- 确认没有多余的空格或特殊字符

### 问题 2：API 连接失败
- 验证 API 密钥是否正确
- 检查 BASE_URL 是否可访问
- 确认网络连接正常

### 问题 3：Milvus 连接问题
- 验证 Milvus 服务器是否运行
- 检查 MILVUS_URI 和 MILVUS_TOKEN 是否正确
- 确认防火墙设置允许连接