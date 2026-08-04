from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .jobs import send_notification_job
from .queue import QueueManager


logger = logging.getLogger(__name__)


def send_notify(
    text: str,
    level: str = 'info',
    extra: Optional[Dict[str, Any]] = None,
    fail_silently: bool = False,
) -> bool:
    """
    Добавляет уведомление в очередь RQ.

    Не блокирует — возвращает управление мгновенно.
    Если очередь переполнена или Redis недоступен — логирует ошибку.
    """

    queue_name = 'notifications_send'

    try:
        return QueueManager.get_instance().enqueue_safe(
            queue_name=queue_name,
            job_func=send_notification_job,
            text=text,
            level=level,
            extra=extra or {},
        )
    except Exception as e:
        if fail_silently:
            logger.error(f'Ошибка добавления в очередь: {e}')
            return False
        raise
