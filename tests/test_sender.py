from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from vk_sender.sender import send_notify


class TestSendNotification:
    """Тесты для send_notify — добавление задач в очередь."""

    @patch('vk_sender.sender.QueueManager')
    def test_success(self, mock_qm):
        """Успешное добавление задачи в очередь."""
        mock_qm.get_instance.return_value.enqueue_safe.return_value = True

        result = send_notify(
            text='Тестовое уведомление',
            level='warning',
            extra={'test': True},
        )

        assert result is True
        mock_qm.get_instance.return_value.enqueue_safe.assert_called_once()

    @patch('vk_sender.sender.QueueManager')
    def test_queue_overflow(self, mock_qm):
        """Очередь переполнена — возвращает False."""
        mock_qm.get_instance.return_value.enqueue_safe.return_value = False

        result = send_notify(
            text='Переполнение',
            level='info',
        )

        assert result is False

    @patch('vk_sender.sender.QueueManager')
    def test_fail_silently_true(self, mock_qm):
        """fail_silently=True — исключение глушится."""
        mock_qm.get_instance.side_effect = RuntimeError('QueueManager не инициализирован')

        result = send_notify(
            text='Ошибка',
            fail_silently=True,
        )

        assert result is False

    @patch('vk_sender.sender.QueueManager')
    def test_fail_silently_false(self, mock_qm):
        """fail_silently=False — исключение пробрасывается."""
        mock_qm.get_instance.side_effect = RuntimeError('QueueManager не инициализирован')

        with pytest.raises(RuntimeError, match='QueueManager не инициализирован'):
            send_notify(
                text='Ошибка',
                fail_silently=False,
            )

    @patch('vk_sender.sender.logger')
    def test_logs_error_on_fail_silently(self, mock_logger):
        """При fail_silently=True ошибка логируется."""
        with patch('vk_sender.sender.QueueManager') as mock_qm:
            mock_qm.get_instance.side_effect = RuntimeError('Redis недоступен')

            result = send_notify(
                text='Test',
                fail_silently=True,
            )

            assert result is False
            mock_logger.error.assert_called_once()
            assert 'Redis недоступен' in mock_logger.error.call_args[0][0]


class TestSendNotificationIntegration:
    """Интеграционные тесты с реальным QueueManager (без Redis)."""

    def test_enqueue_called_with_correct_args(self):
        """Проверяем, что задача ставится с правильными аргументами."""
        with patch('vk_sender.sender.QueueManager') as mock_qm:
            mock_instance = MagicMock()
            mock_qm.get_instance.return_value = mock_instance

            from vk_sender.jobs import send_notification_job

            send_notify(
                text='Важное сообщение',
                level='critical',
                extra={'ip': '192.168.1.1'},
            )

            mock_instance.enqueue_safe.assert_called_once_with(
                queue_name='notifications_send',
                job_func=send_notification_job,
                text='Важное сообщение',
                level='critical',
                extra={'ip': '192.168.1.1'},
            )
