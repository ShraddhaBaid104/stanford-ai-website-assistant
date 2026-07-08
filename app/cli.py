"""
Command Line Interface for the Stanford AI Website Assistant.
"""

from app.rag import StanfordChatbot


def main():
    chatbot = StanfordChatbot()

    print("=" * 60)
    print("Stanford AI Website Assistant")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:
        question = input("\nQuestion: ").strip()

        if not question:
            continue

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        response = chatbot.ask(question)

        print("\nAnswer:\n")
        print(response.answer)

        print("\nSources:")
        for source in response.sources:
            print(f"- {source}")


if __name__ == "__main__":
    main()