from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .backends.vk import VKBackend
from .config import ConfigApp


logger = logging.getLogger(__name__)


class JobContext:
    """
    Контекст выполнения задачи.
    Хранит закэшированные конфиг и бэкенд.
    Создаётся один раз на всё время жизни воркера.
    """

    def __init__(self):
        self._config: Optional[ConfigApp] = None
        self._backend: Optional[VKBackend] = None

    @property
    def config(self) -> ConfigApp:
        """Ленивая загрузка конфига."""
        if self._config is None:
            self._config = ConfigApp.from_django()
            logger.info('Конфиг VK Sender загружен')
        return self._config

    @property
    def backend(self) -> VKBackend:
        """Ленивое создание бэкенда."""
        if self._backend is None:
            vk_config = {
                'TOKEN': self.config.vk_token,
                'ADMINS': self.config.admins,
                'API_VERSION': self.config.vk_api_version,
            }
            self._backend = VKBackend(vk_config)
            logger.info('VKBackend создан')
        return self._backend

    def reset(self) -> None:
        """Сбросить кэш (для тестов)."""
        self._config = None
        self._backend = None
        logger.info('Кэш сброшен')


# Экземпляр на уровне модуля — создаётся один раз при импорте
_context = JobContext()


def send_notification_job(
    text: str,
    level: str = 'info',
    extra: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Задача для RQ-воркера.

    Достаётся из очереди и выполняется в отдельном процессе.
    Отправляет уведомление через VK API.
    """
    try:
        return _context.backend.send(
            text=text,
            level=level,
            extra=extra or {},
        )
    except Exception as e:
        logger.error(f'Ошибка отправки уведомления: {e}', exc_info=True)
        return False


def reset_cache() -> None:
    """Сбросить кэш (для тестов)."""
    _context.reset()
