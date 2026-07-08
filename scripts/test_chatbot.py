from app.rag import StanfordChatbot

chatbot = StanfordChatbot()

question = "How do I apply for undergraduate admission?"

response = chatbot.ask(question)

print("=" * 80)
print("QUESTION")
print("=" * 80)
print(question)

print()

print("=" * 80)
print("ANSWER")
print("=" * 80)
print(response.answer)

print()

print("=" * 80)
print("SOURCES")
print("=" * 80)

for source in response.sources:
    print(source)