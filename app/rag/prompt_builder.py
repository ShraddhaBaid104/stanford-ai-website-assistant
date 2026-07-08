"""
Production Prompt Builder

Responsible for:
- Formatting conversation history
- Formatting retrieved Stanford documents
- Building grounded prompts for the LLM

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from app.models import RetrievedDocument


class PromptBuilder:
    """
    Builds prompts for the Stanford AI Website Assistant.
    """

    SYSTEM_PROMPT = """
You are the Stanford AI Website Assistant.

Your sole responsibility is to answer questions using ONLY the supplied
Stanford website context.

Guidelines:

1. Use ONLY information contained in the provided Stanford context.

2. If the supplied Stanford context does not contain enough information
to answer the user's question confidently, reply exactly:

"I couldn't find that information in the Stanford website content provided."

3. Never invent facts.

4. Never invent URLs.

5. Never use outside knowledge, even if you know the answer.

6. If multiple Stanford documents contain relevant information,
combine them into one coherent answer.

7. Use conversation history ONLY to understand follow-up questions.

8. Never treat conversation history as factual knowledge unless it is
also supported by the supplied Stanford context.

9. Do not include raw URLs in your answer.
The application displays the sources separately.

10. Do not generate citation markers such as [1], [2], or similar.

11. Answer professionally, clearly, accurately, and concisely.

12. Prioritize factual correctness over completeness.
"""

    def build_context(
        self,
        documents: List[RetrievedDocument],
    ) -> str:
        """
        Convert retrieved Stanford documents into a structured context block.
        """

        if not documents:
            return "No relevant Stanford documents were retrieved."

        sections = []

        for index, document in enumerate(documents, start=1):

            sections.append(
                f"""
### Document {index}

Title:
{document.title}

URL:
{document.url}

Content:
{document.content}
""".strip()
            )

        separator = "\n\n" + ("=" * 80) + "\n\n"

        return separator.join(sections)

    def build_conversation_history(
        self,
        history: List[str],
        max_messages: int = 10,
    ) -> str:
        """
        Format recent conversation history.

        Only the latest messages are included to reduce
        token usage.
        """

        if not history:
            return ""

        return "\n".join(history[-max_messages:])

    def build_messages(
        self,
        question: str,
        documents: List[RetrievedDocument],
        conversation_history: List[str],
        summary: str = "",
    ) -> List[BaseMessage]:
        """
        Build the messages sent to the language model.
        """

        context = self.build_context(documents)

        history = self.build_conversation_history(
            conversation_history
        )

        if summary:

            history = f"""
Conversation Summary

{summary}

================================================================================

Recent Conversation

{history}
""".strip()

        history_section = ""

        if history:

            history_section = f"""
Conversation History

{history}

================================================================================

""".strip()

        human_prompt = f"""
{history_section}

Stanford Context

{context}

================================================================================

Current User Question

{question}
""".strip()

        return [
            SystemMessage(
                content=self.SYSTEM_PROMPT.strip(),
            ),
            HumanMessage(
                content=human_prompt,
            ),
        ]