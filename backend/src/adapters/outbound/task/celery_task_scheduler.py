import logging
from datetime import datetime
from typing import Any, Dict, Optional

from celery import Celery
from domain.ports.task_scheduler import TaskScheduler

logger = logging.getLogger(__name__)


class CeleryTaskScheduler(TaskScheduler):
    """
    Adapter implementing the TaskScheduler port using Celery.
    """

    def __init__(self, celery_app: Celery):
        """
        Initialize the CeleryTaskScheduler.

        Args:
            celery_app: The Celery application instance
        """
        self._celery_app = celery_app

    def schedule_task(
        self,
        task_name: str,
        kwargs: Dict[str, Any],
        eta: Optional[datetime] = None,
        queue: Optional[str] = None,
    ) -> str:
        """
        Schedule a task for asynchronous execution using Celery.

        Args:
            task_name: The name of the task to execute
            kwargs: Keyword arguments to pass to the task
            eta: When to execute the task (optional)
            queue: Which queue to use for the task (optional)

        Returns:
            The ID of the scheduled task
        """
        logger.debug(
            f"Scheduling task {task_name} with kwargs: {kwargs}, eta: {eta}, queue: {queue}"
        )

        options = {}
        if eta:
            options["eta"] = eta
        if queue:
            options["queue"] = queue

        # Send task through Celery
        result = self._celery_app.send_task(task_name, kwargs=kwargs, **options)

        logger.info(f"Scheduled task {task_name} with ID {result.id}")
        return result.id
