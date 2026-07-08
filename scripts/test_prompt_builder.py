from app.rag.retrievers.stanford_retriever import StanfordRetriever
from app.rag.prompt_builder import PromptBuilder

retriever = StanfordRetriever(k=3)

builder = PromptBuilder()

question = "How do I apply for undergraduate admission?"

documents = retriever.retrieve(question)

messages = builder.build_messages(
    question=question,
    documents=documents,
)

print("=" * 80)
print("SYSTEM MESSAGE")
print("=" * 80)
print(messages[0].content)

print()

print("=" * 80)
print("HUMAN MESSAGE")
print("=" * 80)
print(messages[1].content)