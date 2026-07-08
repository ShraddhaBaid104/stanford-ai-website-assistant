"""
Test script for the Hybrid Retriever.
"""

from app.rag.retrievers import HybridRetriever


def main():

    retriever = HybridRetriever()

    question = "How do I apply to Stanford?"

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n")

    results = retriever.retrieve(question)

    print("=" * 80)
    print("RESULTS")
    print("=" * 80)

    for index, document in enumerate(results, start=1):

        print(f"\nResult {index}")

        print(f"Title : {document.title}")

        print(f"URL   : {document.url}")

        print(f"Score : {document.score}")

        print(f"ID    : {document.id}")

        print("-" * 80)

        print(document.content[:300])

        print("\n")


if __name__ == "__main__":

    main()