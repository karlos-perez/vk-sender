from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class BaseBackend(ABC):
    """Базовый класс для всех бэкендов отправки уведомлений."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def send(self, text: str, level: str = 'info', extra: Optional[Dict[str, Any]] = None) -> bool:
        """Отправляет уведомление.

        Args:
            text: Основной текст сообщения
            level: Уровень важности (info, warning, error, critical)
            extra: Дополнительная информация

        Returns:
            bool: True, если отправка прошла успешно
        """

    def format_message(self, text: str, level: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Базовое форматирование сообщения. Может быть переопределено в наследниках."""
        emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨',
        }.get(level.lower(), '📌')

        message = f'{emoji} {level.upper()} {self._get_current_time()}\n\n{text}\n'

        if extra:
            message += '\n'

            for key, value in extra.items():
                message += f'{key.capitalize()}: {value}\n'

        return message.strip()

    @staticmethod
    def _get_current_time() -> str:
        """Возвращает текущее время в читаемом формате."""
        dt = datetime.now()  # локальное время сервера
        return f'#{dt.strftime("%Y%m%d_%H%M%S")}'
