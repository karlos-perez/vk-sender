import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class VKSenderConfig(AppConfig):
    name = 'vk_sender'
    label = 'vk_sender'
    verbose_name = _('VK Sender')

    def ready(self) -> None:
        from .config import ConfigApp
        from .queue import QueueManager

        try:
            config = ConfigApp.from_django()
            QueueManager(
                redis_url=config.redis_url,
            )
            logger.info('VK Sender: модуль инициализирован')
        except Exception as e:
            logger.error(f'VK Sender: ошибка инициализации — {e}', exc_info=True)
