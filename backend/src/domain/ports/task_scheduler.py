from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class TaskScheduler(ABC):
    """Port for scheduling asynchronous tasks."""

    @abstractmethod
    def schedule_task(
        self,
        task_name: str,
        kwargs: Dict[str, Any],
        eta: Optional[datetime] = None,
        queue: Optional[str] = None,
    ) -> str:
        """
        Schedule a task for asynchronous execution.

        Args:
            task_name: The name of the task to execute
            kwargs: Keyword arguments to pass to the task
            eta: When to execute the task (optional)
            queue: Which queue to use for the task (optional)

        Returns:
            The ID of the scheduled task
        """
        pass
