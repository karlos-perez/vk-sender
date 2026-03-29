import httpx
import pytest
from unittest.mock import patch, MagicMock

from src.vk_sender.backends.vk import VKBackend
from src.vk_sender.exceptions import VKSenderAPIError, VKSenderConfigError


def test_vk_backend_requires_token(settings):
    """Тест: бэкенд требует TOKEN в конфигурации"""
    config = {
        'ADMINS': [
            {'name': 'Test', 'vk_user_id': 123456789},
        ]
    }

    with pytest.raises(VKSenderConfigError):
        VKBackend(config)


def test_vk_backend_requires_admins(settings):
    """Тест: при отправке должен быть хотя бы один админ"""
    config = {
        'TOKEN': 'test_token_12345',
        'API_VERSION': '5.199',
        'ADMINS': [],
    }

    backend = VKBackend(config)

    with pytest.raises(VKSenderConfigError, match='Список ADMINS пуст'):
        backend.send(text='Тестовое сообщение', level='info')


def test_format_message_basic(settings):
    """Тест базового форматирования сообщения"""
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


def test_format_message_with_different_levels(settings):
    """Тест эмодзи для разных уровней важности"""
    config = {'TOKEN': 'test_token'}
    backend = VKBackend(config)

    levels = ['info', 'warning', 'error', 'critical']
    emojis = ['ℹ️', '⚠️', '❌', '🚨']  # noqa: RUF001

    for level, emoji in zip(levels, emojis, strict=False):
        message = backend.format_message(text='Test', level=level)
        assert emoji in message
        assert level.upper() in message


@patch('httpx.Client')
def test_send_to_user_success(mock_client, settings):
    """Тест успешной отправки сообщения одному пользователю"""
    # Настраиваем мок ответа от VK API
    mock_response = MagicMock()
    mock_response.json.return_value = {'response': 123456}

    # Настраиваем цепочку: Client() -> __enter__() -> post() -> response
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    config = {
        'TOKEN': 'valid_test_token',
        'API_VERSION': '5.199',
        'ADMINS': [
            {'name': 'Test Admin', 'vk_user_id': 123456789},
        ],
    }

    backend = VKBackend(config)
    result = backend._send_to_user(user_id=123456789, message='Тестовое сообщение')

    assert result is True
    mock_client.return_value.__enter__.return_value.post.assert_called_once()


@patch('httpx.Client')
def test_send_to_user_network_error(mock_client, settings):
    """Тест обработки сетевой ошибки"""
    mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException('Connection timeout')

    config = {
        'TOKEN': 'test_token',
        'API_VERSION': '5.199',
        'ADMINS': [
            {'vk_user_id': 123456789},
        ],
    }

    backend = VKBackend(config)

    with pytest.raises(VKSenderAPIError, match='Ошибка сети'):
        backend._send_to_user(user_id=123456789, message='Test')


def test_send_method_success(settings):
    """Тест публичного метода send() — успешная отправка нескольким админам"""
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


def test_send_method_partial_success(settings):
    """Тест: один админ упал — второй отправился успешно"""
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
