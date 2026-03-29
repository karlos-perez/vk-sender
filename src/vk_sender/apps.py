import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VKSenderConfig(AppConfig):
    name = 'vk_sender'
    label = 'vk_sender'
    verbose_name = _('VK Sender')

    def ready(self) -> None:  # noqa: PLR6301
        with contextlib.suppress(Exception):
            from . import sender  # noqa: F401
