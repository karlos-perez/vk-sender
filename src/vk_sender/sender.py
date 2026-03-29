from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.conf import settings

from .backends.vk import VKBackend
from .exceptions import VKSenderConfigError


logger = logging.getLogger(__name__)


def get_backend() -> VKBackend:
    """Возвращает экземпляр бэкенда на основе настроек."""
    notifier_config = getattr(settings, 'VK_SENDER', None)

    if not notifier_config:
        raise VKSenderConfigError('Настройка VK_SENDER не найдена в settings.py')

    vk_config = notifier_config.get('VK', {})
    vk_config['ADMINS'] = notifier_config.get('ADMINS', [])

    return VKBackend(vk_config)


def send_notification(
    text: str, level: str = 'info', extra: Optional[Dict[str, Any]] = None, fail_silently: bool = False
) -> bool:
    """Основная функция для отправки уведомления.

    Args:
        text: Текст сообщения
        level: Уровень важности (info, warning, error, critical)
        extra: Дополнительные данные
        fail_silently: Если True — не будет бросать исключения при ошибках

    Returns:
        bool: True, если хотя бы одно сообщение успешно отправлено
    """
    try:
        backend = get_backend()

        return backend.send(text=text, level=level, extra=extra or {})
    except Exception as e:
        if fail_silently:
            logger.error(f'[VK Sender] Ошибка отправки уведомления: {e}')
            return False
        raise
