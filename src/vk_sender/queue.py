from __future__ import annotations

import logging
from typing import (
    Callable,
    Optional,
)

import redis
import rq


logger = logging.getLogger(__name__)


class QueueManager:
    """
    Синглтон для управления Redis-соединением и очередью RQ.

    Не зависит от Django. Принимает redis_url при инициализации.
    """

    _instance: Optional[QueueManager] = None
    _QUEUE_NAME: str = 'vk_sender'
    _MAX_QUEUE_SIZE: int = 1000

    def __init__(self, redis_url: str):
        if self._instance is not None and hasattr(self, '_redis_url'):
            return

        self._redis_url = redis_url
        self._redis_conn: Optional[redis.Redis] = None
        self._queue: dict = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> QueueManager:
        """Возвращает существующий экземпляр или бросает ошибку, если не инициализирован."""
        if cls._instance is None:
            raise RuntimeError('QueueManager не инициализирован. Сначала вызовите QueueManager(redis_url).')
        return cls._instance

    def _get_redis_connection(self) -> redis.Redis:
        """Ленивое создание подключения к Redis."""
        if self._redis_conn is None:
            try:
                self._redis_conn = redis.Redis.from_url(
                    self._redis_url,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                self._redis_conn.ping()
                logger.info(f'Подключён к Redis ({self._redis_url})')
            except redis.RedisError as e:
                raise ConnectionError(f'Не удалось подключиться к Redis ({self._redis_url}): {e}') from e
        return self._redis_conn

    def get_queue(self, name: Optional[str] = None) -> rq.Queue:
        """Возвращает очередь RQ. Создаёт при первом обращении."""

        if name is None:
            name = self._QUEUE_NAME

        queue = self._queue.get(name)

        if queue is None:
            conn = self._get_redis_connection()
            queue = rq.Queue(
                name,
                connection=conn,
                is_async=True,  # Не падает, если воркер не запущен
            )
            self._queue[name] = queue
            logger.info(f'Очередь {name!r} готова')

        return queue

    def enqueue_safe(self, queue_name: str, job_func: Callable, *args, **kwargs) -> bool:
        """
        Безопасное добавление задачи в очередь.

        Проверяет размер очереди перед добавлением.
        Если очередь переполнена — логирует ошибку и возвращает False.
        """
        queue = self.get_queue(queue_name)

        try:
            queue_size = len(queue)

            if queue_size >= self._MAX_QUEUE_SIZE:
                logger.error(
                    f'Очередь "{queue.name}" переполнена '
                    f'({queue_size}/{self._MAX_QUEUE_SIZE}). '
                    f'Возможно, воркер не запущен.'
                )
                return False

            queue.enqueue(job_func, *args, **kwargs)
            return True

        except redis.RedisError as e:
            logger.error(f'Ошибка Redis при добавлении в очередь: {e}')
            return False
