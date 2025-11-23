__version__ = '1.0.0'
AUTHOR = 'me'
from .config import Config, MilvusConfig   # 把类也暴露出去，方便类型提示
config        = Config()                  # 单例
milvus_config = MilvusConfig()