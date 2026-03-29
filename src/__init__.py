"""
vk-sender — лёгкая Django-батарейка для отправки уведомлений в VK.
"""

from vk_sender.exceptions import VKSenderAPIError, VKSenderConfigError, VKSenderError
from vk_sender.sender import send_notification


__version__ = '0.1.0'
__all__ = ['VKSenderAPIError', 'VKSenderConfigError', 'VKSenderError', 'send_notification']
