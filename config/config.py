import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

"""
全局配置文件，用于管理模型和API配置
"""

class Config:
    # OpenAI API 配置
    # Model settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen3-0.6B-GPTQ-Int8")
    API_KEY: str = os.getenv("API_KEY", "sk-123456")
    BASE_URL: str = os.getenv("BASE_URL", "http://host.docker.internal:8800/v1")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0"))

    deepseek_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_MODEL_NAME: str = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
    deepseek_REASONER_MODEL_NAME: str = os.getenv("DEEPSEEK_REASONER_MODEL_NAME", "deepseek-reasoner")

    EMBEDDINGS_MODEL_NAME: str = os.getenv("EMBEDDINGS_MODEL_NAME", "/model/all-MiniLM-L6-v2")
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "3"))
    max_short_term_messages: int = int(os.getenv("MAX_SHORT_TERM_MESSAGES", "6"))  # sliding window 短期记忆条数




class MilvusConfig:
    # Database Configuration
    MILVUS_URI = os.getenv("MILVUS_URI", "http://192.168.50.3:19530")
    MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", "root:Milvus")
    MILVUS_DATABASE = os.getenv("MILVUS_DATABASE", "rag_db")
    MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "pharma_database")
    MILVUS_TIMEOUT = int(os.getenv("MILVUS_TIMEOUT", "10"))

# 创建配置实例，方便导入使用
config = Config()
milvus_config = MilvusConfig()