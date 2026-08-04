"""
vk-sender — лёгкая Django-батарейка для отправки уведомлений в VK.
"""

from src.vk_sender.exceptions import VKSenderAPIError, VKSenderConfigError, VKSenderError
from src.vk_sender.sender import send_notify


__version__ = '0.1.0'
__all__ = ['VKSenderAPIError', 'VKSenderConfigError', 'VKSenderError', 'send_notify']


default_app_config = 'vk_sender.apps.VKSenderConfig'
