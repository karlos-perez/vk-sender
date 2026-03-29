from __future__ import annotations

from typing import Optional


class VKSenderError(Exception):
    """Базовое исключение для всех ошибок django-vk-sender."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class VKSenderConfigError(VKSenderError):
    """Ошибка конфигурации (отсутствует TOKEN, ADMINS и т.д.)."""

    def __init__(self, message: str = 'Ошибка конфигурации VK Sender'):
        super().__init__(message)


class VKSenderAPIError(VKSenderError):
    """Ошибка при обращении к VK API."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(f'{message} (status={status_code})' if status_code else message)


class VKSenderRateLimitError(VKSenderAPIError):
    """Превышен лимит запросов VK."""

    def __init__(self, message: str = 'Превышен лимит запросов VK API'):
        super().__init__(message, status_code=429)
