from __future__ import annotations

from django.core.management.base import BaseCommand

from vk_sender.sender import send_notify
from vk_sender.jobs import send_notification_job


class Command(BaseCommand):
    help = 'Отправка тестовых уведомлений через VK Sender'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['queue', 'direct'],
            default='queue',
            help='Способ отправки: queue (через Redis) или direct (напрямую)',
        )
        parser.add_argument(
            '--level',
            type=str,
            choices=['info', 'warning', 'error', 'critical'],
            default='info',
            help='Уровень важности',
        )
        parser.add_argument(
            '--text',
            type=str,
            default='Тестовое уведомление от vk-sender',
            help='Текст сообщения',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Отправить сообщения всех уровней',
        )

    def handle(self, **options):
        mode = options['mode']
        level = options['level']
        text = options['text']
        all_levels = options['all']

        if all_levels:
            self._send_all_levels()
            return

        extra = {
            'project': 'vk-sender',
            'environment': 'test',
            'command': 'send_test_notify',
        }

        if mode == 'direct':
            self._send_direct(text, level, extra)
        else:
            self._send_via_queue(text, level, extra)

    def _send_via_queue(self, text: str, level: str, extra: dict):
        """Отправка через Redis-очередь."""
        self.stdout.write('📦 Режим: ЧЕРЕЗ ОЧЕРЕДЬ Redis')
        self.stdout.write(f'   Текст: {text}')
        self.stdout.write(f'   Уровень: {level.upper()}')
        self.stdout.write('')

        try:
            result = send_notify(
                text=text,
                level=level,
                extra=extra,
                fail_silently=False,
            )

            if result:
                self.stdout.write(self.style.SUCCESS('✅ Задача добавлена в очередь'))
                self.stdout.write('')
                self.stdout.write('💡 Для отправки запустите воркер:')
                self.stdout.write('   python manage.py rqworker')
            else:
                self.stdout.write(self.style.WARNING('⚠️  Очередь переполнена, задача не добавлена'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))

    def _send_direct(self, text: str, level: str, extra: dict):
        """Отправка напрямую, минуя очередь."""
        self.stdout.write('📡 Режим: ПРЯМАЯ ОТПРАВКА (без очереди)')
        self.stdout.write(f'   Текст: {text}')
        self.stdout.write(f'   Уровень: {level.upper()}')
        self.stdout.write('')

        try:
            result = send_notification_job(
                text=text,
                level=level,
                extra=extra,
            )

            if result:
                self.stdout.write(self.style.SUCCESS('✅ Сообщение отправлено'))
            else:
                self.stdout.write(self.style.ERROR('❌ Ошибка отправки'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))

    def _send_all_levels(self):
        """Отправка сообщений всех уровней (для полного теста)."""
        levels = ['info', 'warning', 'error', 'critical']
        texts = [
            'ℹ️ Информационное сообщение',
            '⚠️ Предупреждение',
            '❌ Ошибка',
            '🚨 Критическая ошибка',
        ]

        for level, text in zip(levels, texts):
            self.stdout.write(f'Отправка {level.upper()}...', ending=' ')
            try:
                result = send_notify(
                    text=text,
                    level=level,
                    extra={
                        'project': 'vk-sender',
                        'test': 'all_levels',
                    },
                    fail_silently=True,
                )
                if result:
                    self.stdout.write(self.style.SUCCESS('✅'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ {e}'))