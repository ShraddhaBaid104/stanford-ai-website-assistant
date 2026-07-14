from app.rag.retrievers.stanford_retriever import StanfordRetriever

retriever = StanfordRetriever(k=5)

question = "How do I apply for undergraduate admission?"

results = retriever.retrieve_with_scores(question)

print("=" * 80)
print("QUESTION")
print("=" * 80)
print(question)

print()

print("=" * 80)
print("RETRIEVED CHUNKS")
print("=" * 80)

for i, (doc, distance) in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("-" * 80)
    print(f"Distance : {distance:.4f}")
    print(f"Title    : {doc.metadata.get('title')}")
    print(f"URL      : {doc.metadata.get('url')}")
    print()
    print(doc.page_content[:500])