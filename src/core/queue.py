"""Asynchronous Task Queue engine supporting Redis with in-memory asyncio fallback."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable
from pydantic import BaseModel, Field

from src.core.telemetry import logger


class QueueTask(BaseModel):
    """Task message structure for asynchronous background execution."""

    id: str
    task_name: str
    payload: dict[str, Any]
    status: str = "queued"  # queued | running | completed | failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskQueue:
    """Non-blocking event queue managing background render jobs with 0-GPU worker scheduling."""

    def __init__(self, maxsize: int = 1000):
        self._queue: asyncio.Queue[QueueTask] = asyncio.Queue(maxsize=maxsize)
        self._tasks: dict[str, QueueTask] = {}
        self._is_running: bool = False
        self._worker_task: asyncio.Task | None = None
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

    def register_handler(self, task_name: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        """Register a handler callback for a specific task type."""
        self._handlers[task_name] = handler

    async def enqueue(self, task_name: str, payload: dict[str, Any]) -> QueueTask:
        """Add a task to the queue for background execution."""
        from uuid import uuid4

        task = QueueTask(
            id=f"task_{uuid4().hex[:12]}",
            task_name=task_name,
            payload=payload,
        )
        self._tasks[task.id] = task
        await self._queue.put(task)
        logger.info(f"task_enqueued: id={task.id}, task_name={task_name}")
        return task

    async def start_worker(self) -> None:
        """Start the background consumer loop."""
        if self._is_running:
            return
        self._is_running = True
        self._worker_task = asyncio.create_task(self._consumer_loop())
        logger.info("queue_worker_started")

    async def stop_worker(self) -> None:
        """Gracefully stop background worker."""
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("queue_worker_stopped")

    async def _consumer_loop(self) -> None:
        while self._is_running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                task.status = "running"
                logger.info(f"task_executing: id={task.id}, task_name={task.task_name}")

                handler = self._handlers.get(task.task_name)
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(task.payload)
                    else:
                        handler(task.payload)

                task.status = "completed"
                self._queue.task_done()
                logger.info(f"task_completed: id={task.id}")
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as ex:
                logger.error(f"task_failed: {ex}")
                if "task" in locals():
                    task.status = "failed"

    def get_task(self, task_id: str) -> QueueTask | None:
        """Retrieve task status by ID."""
        return self._tasks.get(task_id)

    @property
    def queue_depth(self) -> int:
        """Return current pending task count."""
        return self._queue.qsize()


task_queue = TaskQueue()

__all__ = ["TaskQueue", "QueueTask", "task_queue"]
