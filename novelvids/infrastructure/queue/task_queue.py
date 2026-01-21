"""Task queue implementation."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Any, Callable, Coroutine
from uuid import UUID, uuid4

from loguru import logger


class TaskPriority(IntEnum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 5
    HIGH = 10
    URGENT = 20


@dataclass
class Task:
    """Task representation."""

    id: UUID
    name: str
    payload: dict[str, Any]
    priority: TaskPriority
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None

    def __lt__(self, other: "Task") -> bool:
        """Compare tasks by priority for heap."""
        return self.priority > other.priority


class TaskQueue:
    """In-memory async task queue."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers
        self._queue: asyncio.PriorityQueue[Task] = asyncio.PriorityQueue()
        self._handlers: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._workers: list[asyncio.Task] = []
        self._running = False
        self._tasks: dict[UUID, Task] = {}

    def register_handler(
        self,
        task_name: str,
        handler: Callable[..., Coroutine[Any, Any, Any]],
    ) -> None:
        """Register a handler for a task type."""
        self._handlers[task_name] = handler
        logger.info(f"Registered handler for task: {task_name}")

    async def enqueue(
        self,
        task_name: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> UUID:
        """Enqueue a new task."""
        task = Task(
            id=uuid4(),
            name=task_name,
            payload=payload,
            priority=priority,
            created_at=datetime.utcnow(),
        )
        self._tasks[task.id] = task
        await self._queue.put(task)
        logger.debug(f"Enqueued task {task.id}: {task_name}")
        return task.id

    async def get_task_status(self, task_id: UUID) -> Task | None:
        """Get task status by ID."""
        return self._tasks.get(task_id)

    async def _worker(self, worker_id: int) -> None:
        """Worker coroutine for processing tasks."""
        logger.info(f"Worker {worker_id} started")
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                task.started_at = datetime.utcnow()

                handler = self._handlers.get(task.name)
                if handler is None:
                    logger.error(f"No handler for task: {task.name}")
                    task.error = f"No handler registered for {task.name}"
                    continue

                try:
                    await handler(**task.payload)
                    task.completed_at = datetime.utcnow()
                    logger.info(f"Task {task.id} completed")
                except Exception as e:
                    task.error = str(e)
                    logger.error(f"Task {task.id} failed: {e}")

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")

        logger.info(f"Worker {worker_id} stopped")

    async def start(self) -> None:
        """Start the task queue workers."""
        if self._running:
            return

        self._running = True
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
        logger.info(f"Task queue started with {self.max_workers} workers")

    async def stop(self) -> None:
        """Stop the task queue workers."""
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Task queue stopped")

    @property
    def queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()
