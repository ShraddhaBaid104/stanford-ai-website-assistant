from app.services.memory_service import MemoryService

memory = MemoryService()

session = "demo"

memory.clear(session)

memory.save_user_message(
    session,
    "Hello"
)

memory.save_assistant_message(
    session,
    "Hi!"
)

print(memory.get_history(session))