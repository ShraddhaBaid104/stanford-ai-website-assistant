"""
Collects latency metrics for the conversational pipeline.

Author: Shraddha Nahata
"""

from __future__ import annotations

import time


class MetricsService:

    def __init__(self):

        self.active: dict[str, float] = {}

        self.completed: dict[str, float] = {}

    def start(
        self,
        name: str,
    ) -> None:

        self.active[name] = time.perf_counter()

    def stop(
        self,
        name: str,
    ) -> float:

        start = self.active.pop(
            name,
            None,
        )

        if start is None:
            return 0.0

        elapsed = time.perf_counter() - start

        self.completed[name] = elapsed

        return elapsed

    def get(
        self,
        name: str,
    ) -> float:

        return self.completed.get(
            name,
            0.0,
        )

    def report(
        self,
    ) -> dict[str, float]:

        return self.completed.copy()

    def reset(self):

        self.active.clear()

        self.completed.clear()