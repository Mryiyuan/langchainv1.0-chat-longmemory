"""
交互式对话系统 - DeepSeek + LangGraph + Milvus
"""
import json
import os
from conversation_system import ConversationManager

THREADS_FILE = "saved_threads.json"


# -----------------------------
# 线程管理：读取 / 写入文件
# -----------------------------
def load_threads():
    if os.path.exists(THREADS_FILE):
        with open(THREADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_threads(threads):
    with open(THREADS_FILE, "w", encoding="utf-8") as f:
        json.dump(threads, f, indent=2, ensure_ascii=False)



def view_summary(manager, threads):
    """查看对话总结和记忆"""
    if not threads:
        print("\n❌ 没有对话可以查看")
        return
    
    print("\n📊 对话列表:")
    items = list(threads.items())
    for idx, (tid, info) in enumerate(items, 1):
        print(f"{idx}. {info['name']} (ID: {tid[:8]})")
    
    try:
        choice = int(input("\n选择对话查看总结: "))
    except:
        print("❌ 请输入数字")
        return
    
    if not (1 <= choice <= len(items)):
        print("❌ 无效选择")
        return
    
    thread_id, info = items[choice - 1]
    
    # 获取对话历史 + 长期记忆 + 统计
    history = manager.get_history(thread_id)
    long_term_memory = manager.get_long_term_memory()
    stats = manager.get_thread_stats(thread_id)
    
    print("\n" + "="*60)
    print(f"📋 对话总结 - {info['name']}")
    print("="*60)
    
    # 显示短期记忆
    print("\n📝 对话历史（短期记忆）:")
    print("-"*60)
    if history:
        for i, msg in enumerate(history, 1):
            role = "👤 用户" if msg["role"] == "user" else "🤖 AI"
            content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
            print(f"{i}. {role}: {content}")
    else:
        print("（暂无消息）")
    
    # 显示长期记忆
    print("\n🧠 长期记忆（跨线程）:")
    print("-"*60)
    if long_term_memory:
        for mem in long_term_memory:
            print(f"• {mem}")
    else:
        print("（暂无记忆）")
    
    # 显示统计
    print(f"\n📊 统计:")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  用户消息: {stats['user_messages']}")
    print(f"  AI回复: {stats['ai_messages']}")
    print(f"  对话轮次: {stats['turns']}")
    print("="*60 + "\n")
# -----------------------------
# 菜单界面
# -----------------------------
def print_menu():
    """打印菜单"""
    print("\n" + "=" * 60)
    print("🤖 AI 对话系统 - LangGraph + Milvus + DeepSeek")
    print("="*60)
    print("\n📋 菜单:")
    print("  1️⃣  新建对话")
    print("  2️⃣  继续对话")
    print("  3️⃣  查看对话总结  ← 新增")
    print("  4️⃣  查看历史对话")
    print("  5️⃣  删除对话")
    print("  6️⃣  退出")
    print("\n" + "-"*60)

# -----------------------------
# 业务逻辑
# -----------------------------
def create_new_conversation(manager, threads):
    print("\n📝 创建新对话")
    name = input("输入对话名称（默认：未命名）: ").strip() or "未命名"

    thread_id = manager.create_thread()
    threads[thread_id] = {"name": name}
    save_threads(threads)

    print(f"✨ 已创建，ID: {thread_id[:8]}...")
    chat_in_thread(manager, thread_id)


def continue_conversation(manager, threads):
    if not threads:
        print("\n⚠️ 没有保存的对话")
        return

    print("\n📚 已保存的对话：")
    items = list(threads.items())
    for idx, (tid, info) in enumerate(items, 1):
        print(f"{idx}. {info['name']} (ID: {tid[:8]})")

    try:
        choice = int(input("\n选择对话编号: "))
    except:
        print("❌ 请输入数字")
        return

    if not (1 <= choice <= len(items)):
        print("❌ 无效选择")
        return

    thread_id, _ = items[choice - 1]
    chat_in_thread(manager, thread_id)


def chat_in_thread(manager, thread_id):
    print(f"\n💬 开始对话（ID: {thread_id[:8]}）")
    print("输入 'exit' 退出此对话\n")

    while True:
        user_input = input("你: ").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            print("🔙 返回菜单\n")
            break

        print("AI: ", end="", flush=True)

        try:
            for chunk in manager.stream_message(thread_id, user_input):
                print(chunk, end="", flush=True)
            print("\n")

        except Exception as e:
            print(f"\n❌ 出错: {e}")
            break


def view_history(manager, threads):
    if not threads:
        print("\n⚠️ 没有对话可查看")
        return

    print("\n📚 对话列表:")
    items = list(threads.items())
    for idx, (tid, info) in enumerate(items, 1):
        print(f"{idx}. {info['name']}")

    try:
        choice = int(input("\n选择编号查看历史: "))
    except:
        print("❌ 请输入数字")
        return

    if not (1 <= choice <= len(items)):
        print("❌ 无效编号")
        return

    thread_id, info = items[choice - 1]
    history = manager.get_history(thread_id)

    print(f"\n📜 对话历史 - {info['name']}")
    print("-" * 60)

    for msg in history:
        role = "👤 用户" if msg["role"] == "user" else "🤖 AI"
        print(f"{role}: {msg['content']}\n")


def delete_conversation(threads):
    if not threads:
        print("\n⚠️ 没有对话可以删除")
        return

    print("\n🗑 删除对话")
    items = list(threads.items())
    for idx, (tid, info) in enumerate(items, 1):
        print(f"{idx}. {info['name']} (ID: {tid[:8]})")

    try:
        choice = int(input("\n要删除哪个（编号）: "))
    except:
        print("❌ 请输入数字")
        return

    if not (1 <= choice <= len(items)):
        print("❌ 无效编号")
        return

    thread_id, info = items[choice - 1]

    if input(f"确认删除 '{info['name']}' ? (y/n): ").lower() == "y":
        del threads[thread_id]
        save_threads(threads)
        print("🗑 已删除\n")
    else:
        print("❌ 取消删除\n")


# -----------------------------
# 主函数
# -----------------------------
def main():
    print("⏳ 初始化对话系统...")
    manager = ConversationManager()
    threads = load_threads()

    print("✅ 系统已就绪!\n")

    while True:
        print_menu()
        cmd = input("选择操作: ").strip()

        if cmd == "1":
            create_new_conversation(manager, threads)
        elif cmd == "2":
            continue_conversation(manager, threads)
        elif cmd == "3":
            view_summary(manager, threads)  # 新增
        elif cmd == "4":
            view_history(manager, threads)
        elif cmd == "5":
            delete_conversation(threads)
        elif cmd == "6":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请输入 1~6")

if __name__ == "__main__":
    main()
