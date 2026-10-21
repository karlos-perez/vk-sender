from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


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

    def format_message(self, text: str, level: str, extra: Optional[Union[Dict[str, Any], List[str]]] = None) -> str:
        """Базовое форматирование сообщения. Может быть переопределено в наследниках."""
        emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨',
        }.get(level.lower(), '📌')

        body = f'{emoji} {level.upper()} {self._get_current_time()}\n\n{text}\n'

        if extra:
            extra_text = self._make_extra(extra)

            if extra_text:
                message = f'{body}\n{extra_text}'

        return message.strip()

    @staticmethod
    def _get_current_time() -> str:
        """Возвращает текущее время в читаемом формате."""
        dt = datetime.now()  # локальное время сервера
        return f'#{dt.strftime("%Y%m%d_%H%M%S")}'

    @staticmethod
    def _make_extra(extra: Union[Dict[str, Any], List[str]]) -> str:
        """Собираем дополнительный текст"""

        if isinstance(extra, dict):
            text = [f'{key}: {value}\n' for key, value in extra.items()]
        elif isinstance(extra, list):
            text = extra
        else:
            return ''

        return '\n'.join(text)