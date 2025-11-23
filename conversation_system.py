import sqlite3
import uuid
from typing import TypedDict, List

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  # ← 加这个

from embeddings_model import get_embeddings
from config import config, milvus_config

from langchain_openai import ChatOpenAI
from langchain_milvus import Milvus


# ============================================
# 定义状态（给 LangGraph 用）
# ============================================
class ConversationState(TypedDict):
    messages: List[BaseMessage]


# ============================================
# 初始化 SQLite 数据库
# ============================================
def init_db():
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            thread_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


# ============================================
# 初始化 LLM
# ============================================
def init_llm():
    return ChatOpenAI(
        model=config.deepseek_REASONER_MODEL_NAME,
        api_key=config.deepseek_API_KEY,
        base_url=config.deepseek_BASE_URL,
        temperature=0.7,
    )


# ============================================
# 初始化 Milvus
# ============================================
def init_vector_store():
    embeddings = get_embeddings()
    return Milvus(
        embedding_function=embeddings,
        connection_args={"uri": milvus_config.MILVUS_URI},
        collection_name="user_memories",
        index_params={"index_type": "HNSW", "metric_type": "L2"},
        auto_id=True,
    )


# ============================================
# SQLite 操作
# ============================================
def save_message(thread_id: str, role: str, content: str):
    """保存消息到 SQLite"""
    try:
        conn = sqlite3.connect("conversations.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
            (thread_id, role, content)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 保存消息失败: {e}")


def load_messages(thread_id: str) -> List[BaseMessage]:
    """从 SQLite 加载消息"""
    try:
        conn = sqlite3.connect("conversations.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE thread_id = ? ORDER BY id",
            (thread_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for role, content in rows:
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        
        return messages
    except Exception as e:
        print(f"❌ 加载消息失败: {e}")
        return []


def get_message_count(thread_id: str) -> int:
    """获取某个线程的消息数"""
    try:
        conn = sqlite3.connect("conversations.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE thread_id = ?",
            (thread_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


# ============================================
# 长期记忆检索
# ============================================
def retrieve_memory(query: str, vector_store: Milvus) -> str:
    try:
        docs = vector_store.similarity_search(query, k=3)
        if not docs:
            return ""
        return "\n".join(f"- {d.page_content}" for d in docs)
    except:
        return ""


# ============================================
# LLM 节点（给 LangGraph 用）
# ============================================
def llm_node(state: ConversationState, vector_store) -> dict:
    """LLM 处理节点"""
    llm = init_llm()
    
    # 获取最后一条用户消息
    last_user_msg = state["messages"][-1].content
    
    # 从长期记忆检索
    long_term_memory = retrieve_memory(last_user_msg, vector_store)

    system_prompt = f"""你是一个有记忆的智能助手。

=== 长期记忆（跨线程） ===
{long_term_memory if long_term_memory else "（暂无相关记忆）"}

=== 对话指引 ===
- 基于对话历史和长期记忆回答
- 识别并记住用户的重要信息
- 保持友好、专业的语态"""

    # 只用最近 6 条消息
    short_window = state["messages"][-6:]

    response = llm.invoke(
        [SystemMessage(content=system_prompt)] + short_window
    )

    return {"messages": [response]}


# ============================================
# 构建 LangGraph（用于 MemorySaver）
# ============================================
def build_graph(vector_store):
    """构建对话图，使用 MemorySaver 做短期记忆"""
    builder = StateGraph(ConversationState)
    
    builder.add_node("llm", lambda s: llm_node(s, vector_store))
    builder.add_edge(START, "llm")
    builder.add_edge("llm", END)
    
    # ✅ 用 MemorySaver 做短期记忆（程序运行期间）
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    
    return graph


# ============================================
# 是否需要保存长期记忆（用 LLM 智能判断）
# ============================================
def should_store_memory(text: str, vector_store) -> bool:
    """用 LLM 判断是否包含重要个人信息"""
    llm = init_llm()
    
    judge_prompt = f"""判断以下用户消息是否包含重要的个人信息（名字、工作、爱好、经历等）。
只有包含"用户本人的重要信息"才返回"是"。不要保存关于天气、食物等一般性话题。

用户消息: {text}

请回答"是"或"否"，只返回一个字："""

    try:
        response = llm.invoke(judge_prompt).content.strip()
        return "是" in response
    except:
        return False


def extract_memory(text: str, vector_store) -> str:
    """用 LLM 提取重要信息"""
    llm = init_llm()
    
    extract_prompt = f"""从以下用户消息中提取重要的个人信息。
如果没有重要信息，返回"无"。

用户消息: {text}

请提取信息（格式自由）或返回"无"："""

    try:
        response = llm.invoke(extract_prompt).content.strip()
        if response != "无":
            return response
        return None
    except:
        return None


# ============================================
# ConversationManager
# ============================================
class ConversationManager:

    def __init__(self):
        init_db()
        self.vector_store = init_vector_store()
        # ✅ 用 LangGraph + MemorySaver 做短期记忆
        self.graph = build_graph(self.vector_store)

    def create_thread(self) -> str:
        return str(uuid.uuid4())

    def stream_message(self, thread_id: str, text: str):
        """流式输出消息"""
        config = {"configurable": {"thread_id": thread_id}}
        
        # ✅ 方案 1：先从 SQLite 加载历史
        previous_messages = load_messages(thread_id)
        
        # 合并历史 + 新消息
        all_messages = previous_messages + [HumanMessage(content=text)]
        
        # ✅ 方案 2：用 LangGraph + MemorySaver 处理当前会话
        # （LangGraph 会自动用 MemorySaver 保存状态在内存中）
        full_response = ""
        for event in self.graph.stream(
            {"messages": all_messages},
            config,
            stream_mode="values"
        ):
            if "messages" in event:
                msg = event["messages"][-1]
                if isinstance(msg, AIMessage):
                    # 流式输出
                    for chunk in msg.content:
                        yield chunk
                        full_response += chunk
        
        # ✅ 方案 3：保存到 SQLite（持久化）
        save_message(thread_id, "user", text)
        save_message(thread_id, "assistant", full_response)
        
        # ✅ 方案 4：保存长期记忆到 Milvus（跨线程）
        if should_store_memory(text, self.vector_store):
            memory = extract_memory(text, self.vector_store)
            if memory:
                try:
                    self.vector_store.add_documents([
                        Document(page_content=memory)
                    ])
                    print(f"💾 已保存长期记忆: {memory[:50]}...")
                except:
                    pass

    def get_history(self, thread_id: str) -> list:
        """获取对话历史"""
        messages = load_messages(thread_id)
        
        result = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                result.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                result.append({"role": "assistant", "content": msg.content})
        
        return result

    def get_long_term_memory(self) -> list:
        """获取所有长期记忆"""
        try:
            docs = self.vector_store.similarity_search("用户", k=20)
            return [d.page_content for d in docs]
        except:
            return []
    
    def get_thread_stats(self, thread_id: str) -> dict:
        """获取对话统计"""
        messages = load_messages(thread_id)
        user_count = len([m for m in messages if isinstance(m, HumanMessage)])
        ai_count = len([m for m in messages if isinstance(m, AIMessage)])
        
        return {
            "total_messages": len(messages),
            "user_messages": user_count,
            "ai_messages": ai_count,
            "turns": user_count
        }