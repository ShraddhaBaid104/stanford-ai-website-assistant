"""
Prompt Injection Guard

Detects common prompt injection attempts before
the request reaches the language model.
"""

from __future__ import annotations


class PromptInjectionGuard:

    BLOCKED_PATTERNS = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "forget previous instructions",
        "forget the above",
        "system prompt",
        "hidden prompt",
        "developer message",
        "developer instructions",
        "reveal your prompt",
        "show your prompt",
        "show system prompt",
        "print your instructions",
        "repeat your instructions",
        "jailbreak",
        "act as",
        "pretend to be",
        "you are chatgpt",
        "you are now",
        "bypass",
        "override",
        "disable safety",
    ]

    def is_prompt_injection(
        self,
        question: str,
    ) -> bool:

        question = question.lower()

        return any(
            pattern in question
            for pattern in self.BLOCKED_PATTERNS
        )

    @staticmethod
    def fallback_message() -> str:

        return (
            "I can't follow instructions that attempt to "
            "change my behavior or reveal my internal instructions. "
            "Please ask a question about Stanford University."
        )