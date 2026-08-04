from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from vk_sender.backends.vk import VKBackend
from vk_sender.exceptions import VKSenderAPIError, VKSenderConfigError


class TestVKBackendInit:
    """Тесты инициализации VKBackend."""

    def test_requires_token(self):
        """Бэкенд требует TOKEN в конфигурации."""
        config = {
            'ADMINS': [{'name': 'Test', 'vk_user_id': 123456789}],
        }

        with pytest.raises(VKSenderConfigError):
            VKBackend(config)

    def test_requires_admins(self):
        """При отправке должен быть хотя бы один админ."""
        config = {
            'TOKEN': 'test_token_12345',
            'API_VERSION': '5.199',
            'ADMINS': [],
        }

        backend = VKBackend(config)

        with pytest.raises(VKSenderConfigError, match='Список ADMINS пуст'):
            backend.send(text='Тестовое сообщение', level='info')

    def test_default_api_version(self):
        """Если API_VERSION не указан — используется 5.131."""
        config = {
            'TOKEN': 'test_token',
            'ADMINS': [{'name': 'Admin', 'vk_user_id': 123}],
        }
        backend = VKBackend(config)
        assert backend.api_version == '5.199'


class TestFormatMessage:
    """Тесты форматирования сообщений."""

    def test_basic(self):
        """Базовое форматирование сообщения."""
        config = {'TOKEN': 'test_token'}
        backend = VKBackend(config)

        message = backend.format_message(
            text='Сервер недоступен',
            level='critical',
            extra={'project': 'crm', 'environment': 'production'},
        )

        assert '🚨 CRITICAL #' in message
        assert 'Сервер недоступен' in message
        assert 'Project: crm' in message
        assert 'Environment: production' in message

    def test_different_levels(self):
        """Эмодзи для разных уровней важности."""
        config = {'TOKEN': 'test_token'}
        backend = VKBackend(config)

        levels = ['info', 'warning', 'error', 'critical']
        emojis = ['ℹ️', '⚠️', '❌', '🚨']

        for level, emoji in zip(levels, emojis):
            message = backend.format_message(text='Test', level=level)
            assert emoji in message
            assert level.upper() in message

    def test_without_extra(self):
        """Без дополнительных данных — не ломается."""
        config = {'TOKEN': 'test_token'}
        backend = VKBackend(config)

        message = backend.format_message(text='Test', level='info')
        assert 'Test' in message
        assert 'INFO' in message

    def test_with_empty_extra(self):
        """Пустой extra — не добавляет лишних полей."""
        config = {'TOKEN': 'test_token'}
        backend = VKBackend(config)

        message = backend.format_message(text='Test', level='info', extra={})
        assert 'Project:' not in message


class TestSendToUser:
    """Тесты метода _send_to_user."""

    @patch('httpx.Client')
    def test_success(self, mock_client):
        """Успешная отправка одному пользователю."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 123456}
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response

        config = {
            'TOKEN': 'valid_test_token',
            'API_VERSION': '5.199',
            'ADMINS': [{'name': 'Test Admin', 'vk_user_id': 123456789}],
        }

        backend = VKBackend(config)
        result = backend._send_to_user(user_id=123456789, message='Тестовое сообщение')

        assert result is True
        mock_client.return_value.__enter__.return_value.post.assert_called_once()

    @patch('httpx.Client')
    def test_network_error(self, mock_client):
        """Обработка сетевой ошибки."""
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException('Connection timeout')

        config = {
            'TOKEN': 'test_token',
            'API_VERSION': '5.199',
            'ADMINS': [{'vk_user_id': 123456789}],
        }

        backend = VKBackend(config)

        with pytest.raises(VKSenderAPIError, match='Ошибка сети'):
            backend._send_to_user(user_id=123456789, message='Test')

    @patch('httpx.Client')
    def test_api_error(self, mock_client):
        """Обработка ошибки от VK API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'error': {
                'error_code': 5,
                'error_msg': 'User authorization failed',
            }
        }
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response

        config = {
            'TOKEN': 'test_token',
            'API_VERSION': '5.199',
            'ADMINS': [{'vk_user_id': 123456789}],
        }

        backend = VKBackend(config)

        with pytest.raises(VKSenderAPIError, match='VK API Error'):
            backend._send_to_user(user_id=123456789, message='Test')


class TestSendMethod:
    """Тесты публичного метода send."""

    def test_success_multiple_admins(self):
        """Успешная отправка нескольким админам."""
        config = {
            'TOKEN': 'test_token',
            'API_VERSION': '5.199',
            'ADMINS': [
                {'name': 'Admin1', 'vk_user_id': 111111},
                {'name': 'Admin2', 'vk_user_id': 222222},
            ],
        }

        backend = VKBackend(config)

        with patch.object(backend, '_send_to_user', return_value=True) as mock_send:
            result = backend.send(
                text='Важное уведомление',
                level='error',
                extra={'project': 'shop'},
            )

            assert result is True
            assert mock_send.call_count == 2

    def test_partial_success(self):
        """Один админ упал — второй отправился успешно."""
        config = {
            'TOKEN': 'test_token',
            'ADMINS': [
                {'name': 'Bad', 'vk_user_id': 111},
                {'name': 'Good', 'vk_user_id': 222},
            ],
        }

        backend = VKBackend(config)

        def side_effect(user_id, message):
            if user_id == 111:
                raise Exception('Failed')
            return True

        with patch.object(backend, '_send_to_user', side_effect=side_effect):
            result = backend.send(
                text='Тест частичного успеха',
                level='warning',
            )

            assert result is True

    def test_all_failed(self):
        """Все админы упали — возвращает False."""
        config = {
            'TOKEN': 'test_token',
            'ADMINS': [
                {'name': 'Bad1', 'vk_user_id': 111},
                {'name': 'Bad2', 'vk_user_id': 222},
            ],
        }

        backend = VKBackend(config)

        with patch.object(backend, '_send_to_user', side_effect=Exception('Fail')):
            with patch('vk_sender.backends.vk.logger') as mock_logger:
                result = backend.send(
                    text='Никто не получит',
                    level='critical',
                )

                assert result is False
                # Проверяем что ошибки залогированы (по одному на каждого админа)
                assert mock_logger.error.call_count == 2
                # Проверяем текст последней ошибки
                mock_logger.error.assert_called_with(
                    '[VK Sender] Ошибка отправки пользователю user_id=222: Fail',
                )
