import pytest
from unittest.mock import patch, MagicMock

from src.vk_sender.sender import send_notification, get_backend
from src.vk_sender.exceptions import VKSenderConfigError
from src.vk_sender.backends.vk import VKBackend


def test_get_backend_success(settings):
    """Тест получения бэкенда"""
    backend = get_backend()
    assert isinstance(backend, VKBackend)


def test_send_notification_success(settings):
    """Тест успешной отправки уведомления"""
    with patch('src.vk_sender.sender.get_backend') as mock_get_backend:
        mock_backend = MagicMock()
        mock_backend.send.return_value = True
        mock_get_backend.return_value = mock_backend

        result = send_notification(text='Тестовое уведомление', level='warning', extra={'test': True})

        assert result is True
        mock_backend.send.assert_called_once()


def test_send_notification_fail_silently(settings):
    """Тест fail_silently=True"""
    with patch('src.vk_sender.sender.get_backend', side_effect=Exception('Test error')):
        result = send_notification(text='Ошибка', fail_silently=True)
        assert result is False


def test_send_notification_raises_without_fail_silently(settings):
    """Тест, что исключение поднимается, если fail_silently=False"""
    with (
        patch('src.vk_sender.sender.get_backend', side_effect=VKSenderConfigError('No config')),
        pytest.raises(VKSenderConfigError),
    ):
        send_notification('Ошибка', fail_silently=False)


def test_send_notification_with_empty_admins(settings):
    """Тест поведения при пустом списке ADMINS"""
    # Переопределяем настройки без ADMINS
    from django.conf import settings

    settings.VK_SENDER['ADMINS'] = []

    with pytest.raises(VKSenderConfigError):
        send_notification('Тест без админов')
