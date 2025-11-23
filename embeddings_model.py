from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from config import config

class LocalEmbeddings(Embeddings):
    """使用 sentence-transformers 的本地 embeddings，适合 RTX 3070"""
    
    def __init__(self, model_name: str = config.EMBEDDINGS_MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        # RTX 3070 用 GPU
        try:
            self.model.cuda()
            self.device = "cuda"
        except:
            self.device = "cpu"
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """嵌入文档列表"""
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    def embed_query(self, text: str) -> list[float]:
        """嵌入单个查询"""
        return self.model.encode(text, convert_to_numpy=True).tolist()


# 全局 embeddings 实例（延迟初始化）
_embeddings_instance = None

def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        print("🔄 初始化 Embeddings 模型（首次启动会下载 ~380MB）...")
        _embeddings_instance = LocalEmbeddings()
        print("✅ Embeddings 模型加载完成")
    return _embeddings_instance