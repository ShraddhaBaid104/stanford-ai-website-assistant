from app.memory.redis_memory import RedisMemory

memory = RedisMemory()

session = "demo"

memory.clear(session)

memory.add_user_message(
    session,
    "What is Stanford?"
)

memory.add_assistant_message(
    session,
    "Stanford University is..."
)

history = memory.get_history(session)

print(history)