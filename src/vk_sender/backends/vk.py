from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from ..exceptions import VKSenderAPIError, VKSenderConfigError
from .base import BaseBackend


logger = logging.getLogger(__name__)


class VKBackend(BaseBackend):
    """Бэкенд для отправки уведомлений через VK API (метод messages.send)."""

    _URL_MESSAGE_SEND = 'https://api.vk.com/method/messages.send'

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get('TOKEN')
        self.api_version = config.get('API_VERSION', '5.199')
        self.group_id = config.get('GROUP_ID')

        if not self.token:
            raise VKSenderConfigError('VK.TOKEN не указан в настройках')

    def send(self, text: str, level: str = 'info', extra: Optional[Dict[str, Any]] = None) -> bool:
        """Отправляет сообщение указанным администраторам."""
        message = self.format_message(text, level, extra)
        admins = self.config.get('ADMINS', [])

        if not admins:
            raise VKSenderConfigError('Список ADMINS пуст или не указан')

        success_count = 0

        for admin in admins:
            user_id = admin.get('vk_user_id')
            if not user_id:
                continue

            try:
                if self._send_to_user(user_id, message):
                    success_count += 1
            except Exception as e:
                logger.error(f'[VK Sender] Ошибка отправки пользователю {user_id=}: {e}')

        return success_count > 0

    def _send_to_user(self, user_id: int, message: str) -> bool:
        """Отправка сообщения одному пользователю."""

        params = {
            'access_token': self.token,
            'v': self.api_version,
            'user_id': user_id,
            'message': message,
            'random_id': self._generate_random_id(),
        }

        # Если указан GROUP_ID — отправляем от имени группы
        if self.group_id:
            params['peer_id'] = f'-{self.group_id}'

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self._URL_MESSAGE_SEND, params=params)
                data = response.json()

                if 'error' in data:
                    error_msg = data['error'].get('error_msg', 'Unknown error')
                    error_code = data['error'].get('error_code')
                    raise VKSenderAPIError(f'VK API Error: {error_msg}', status_code=error_code)

                return True

        except httpx.RequestError as err:
            raise VKSenderAPIError(f'Ошибка сети при обращении к VK API: {err}') from err

    @staticmethod
    def _generate_random_id() -> int:
        """Генерирует случайный id для сообщения (требуется VK API)."""
        import random

        return random.randint(1, 2_147_483_647)
