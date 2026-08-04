from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AdminConfig:
    name: str
    vk_user_id: int


@dataclass(frozen=True)
class ConfigApp:
    """Настройки модуля vk_sender, загружаемые из settings.VK_SENDER."""

    # VK API
    vk_token: str
    vk_api_version: str
    # Администраторы
    admins: List[AdminConfig]
    # Redis для очереди
    redis_url: str
    default_timeout: int

    @classmethod
    def from_django(cls) -> ConfigApp:
        raw: Dict[str, Any] = getattr(settings, 'VK_SENDER', None)

        if not raw:
            raise ImproperlyConfigured(
                'VK_SENDER не найден в settings.py. Добавьте словарь с ключами ADMINS, VK, RQ_QUEUES.'
            )

        # --- Админы ---
        admins_list = raw.get('ADMINS', [])

        if not admins_list:
            raise ImproperlyConfigured('VK_SENDER["ADMINS"] не может быть пустым')

        admins = [AdminConfig(name=a['name'], vk_user_id=a['vk_user_id']) for a in admins_list]

        # --- VK ---
        vk = raw.get('VK', {})

        if not vk:
            raise ImproperlyConfigured('VK_SENDER["VK"] обязателен')

        token = vk.get('TOKEN')

        if not token:
            raise ImproperlyConfigured('VK_SENDER["VK"]["TOKEN"] обязателен')

        api_version = vk.get('API_VERSION', '5.199')

        # --- RQ (Redis) ---
        rq_queues = raw.get('RQ_QUEUES', {})

        if not rq_queues:
            raise ImproperlyConfigured(
                'VK_SENDER["RQ_QUEUES"] обязателен. Добавьте настройки подключения к Redis для очереди.'
            )

        # Ищем конфиг для очереди 'notifications_send'
        queue_config = rq_queues.get('notifications_send', {})

        if not queue_config:
            raise ImproperlyConfigured('VK_SENDER["RQ_QUEUES"]["notifications_send"] не найден.')

        redis_host = queue_config.get('HOST', 'localhost')
        redis_port = int(queue_config.get('PORT', 6379))
        redis_db = int(queue_config.get('DB', 1))
        default_timeout = int(queue_config.get('DEFAULT_TIMEOUT', 60))

        logger.info('VKSenderConfig успешно загружен')

        return cls(
            vk_token=token,
            vk_api_version=api_version,
            admins=admins,
            redis_url=f'redis://{redis_host}:{redis_port}/{redis_db}',
            default_timeout=default_timeout,
        )
