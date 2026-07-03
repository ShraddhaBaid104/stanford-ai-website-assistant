"""
Production Prompt Builder

Responsible for:
- Formatting retrieved documents into context
- Building the system prompt
- Building the final messages for the LLM

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage


class PromptBuilder:
    """
    Builds grounded prompts for the Stanford AI Website Assistant.
    """

    SYSTEM_PROMPT = """
You are the Stanford AI Website Assistant.

Your job is to answer questions using ONLY the provided context.

Rules:

1. Use ONLY the information contained in the context.

2. If the answer is not available in the context,
   say:

   "I couldn't find that information in the Stanford website content provided."

3. Never make up facts.

4. Never invent URLs.

5. If multiple sources contain relevant information,
   combine them into one clear answer.

6. Be concise, accurate and professional.

7. Do not include source URLs in your answer.
   The application will display the sources separately.
"""

    def build_context(
        self,
        documents: List[Document],
    ) -> str:
        """
        Convert retrieved documents into a formatted context block.
        """

        sections = []

        for i, doc in enumerate(documents, start=1):

            title = doc.metadata.get("title", "Unknown")
            url = doc.metadata.get("url", "Unknown")

            section = f"""
Source {i}

Title:
{title}

URL:
{url}

Content:
{doc.page_content}
"""

            sections.append(section.strip())

        return "\n\n" + ("\n\n" + "=" * 80 + "\n\n").join(sections)

    def build_messages(
        self,
        question: str,
        documents: List[Document],
    ):
        """
        Build LangChain chat messages.
        """

        context = self.build_context(documents)

        human_prompt = f"""
Context

{context}

----------------------------------------

Question

{question}
"""

        return [
            SystemMessage(content=self.SYSTEM_PROMPT.strip()),
            HumanMessage(content=human_prompt.strip()),
        ]