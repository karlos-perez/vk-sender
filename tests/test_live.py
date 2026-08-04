"""
Живое тестирование vk-sender.
Отправляет реальные сообщения в VK.

Запуск:
    # С Redis в Docker (очередь + воркер)
    docker-compose up -d redis worker
    python tests/test_live.py --user 123456789 --token your_token

    # Без Redis (прямая отправка, мокаем очередь)
    python tests/test_live.py --user 123456789 --token your_token --direct

    # Параметры можно передать как позиционные:
    python tests/test_live.py 123456789 your_token
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

import django
from django.conf import settings


def parse_args():
    parser = argparse.ArgumentParser(description='Тест: Отправка реальных сообщений в VK')
    parser.add_argument('--user', type=int, help='Идентификатор пользователя VK')
    parser.add_argument('--token', help='Токен VK')
    parser.add_argument('--direct', action='store_true', help='Отправка напрямую, без очереди Redis')
    parser.add_argument('vk_user_id', nargs='?', type=int, help=argparse.SUPPRESS)
    parser.add_argument('vk_token', nargs='?', help=argparse.SUPPRESS)

    args = parser.parse_args()

    user_id = args.user or args.vk_user_id
    token = args.token or args.vk_token

    if not user_id or not token:
        parser.error('Необходимо указать --user и --token')

    return user_id, token, args.direct


def setup_django(user_id: int, token: str, use_redis: bool = True):
    """Настройка Django с тестовыми параметрами."""

    redis_config = {}
    if use_redis:
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        redis_config = {
            'RQ_QUEUES': {
                'notifications_send': {
                    'HOST': redis_host,
                    'PORT': redis_port,
                    'DB': 1,
                    'DEFAULT_TIMEOUT': 60,
                },
            },
        }

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={},
            INSTALLED_APPS=[
                'vk_sender',
            ],
            USE_TZ=True,
            TIME_ZONE='UTC',
            SECRET_KEY='test-live-secret-key',
            VK_SENDER={
                'ADMINS': [
                    {
                        'name': 'Тестовый Админ',
                        'vk_user_id': user_id,
                    },
                ],
                'VK': {
                    'TOKEN': token,
                    'API_VERSION': '5.199',
                },
                **redis_config,
            },
        )

    django.setup()


def run_direct(user_id: int, token: str):
    """Прямая отправка — без Django, без Redis, без очереди."""
    from vk_sender.backends.vk import VKBackend

    print('📡 Режим: ПРЯМАЯ ОТПРАВКА (без очереди)\n')

    backend = VKBackend(
        {
            'TOKEN': token,
            'API_VERSION': '5.199',
            'ADMINS': [{'name': 'Тестовый Админ', 'vk_user_id': user_id}],
        }
    )

    test_cases = [
        ('info', 'ℹ️ Это тестовое информационное сообщение'),
        ('warning', '⚠️ Внимание: заканчивается место на диске'),
        ('error', '❌ Ошибка при обработке заказа #12345'),
        ('critical', '🚨 КРИТИЧНО: Приложение упало! Сервер недоступен'),
    ]

    for level, text in test_cases:
        print(f'Отправляем: {level.upper()}...', end=' ')
        try:
            result = backend.send(
                text=text,
                level=level,
                extra={
                    'project': 'vk-sender',
                    'environment': 'test',
                    'mode': 'direct',
                },
            )
            print('✅' if result else '⚠️  Не отправлено')
        except Exception as e:
            print(f'❌ Ошибка: {e}')
        print('-' * 60)


def run_with_queue(user_id: int, token: str):
    """Отправка через очередь Redis."""
    from vk_sender.sender import send_notify

    print('📦 Режим: ЧЕРЕЗ ОЧЕРЕДЬ Redis\n')
    print('⚠️  Убедитесь, что Redis запущен и воркер активен:')
    print('   docker-compose up -d redis worker')
    print('   или: python manage.py rqworker --queue=notifications_send\n')

    test_cases = [
        ('info', 'ℹ️ Это тестовое информационное сообщение'),
        ('warning', '⚠️ Внимание: заканчивается место на диске'),
        ('error', '❌ Ошибка при обработке заказа #12345'),
        ('critical', '🚨 КРИТИЧНО: Приложение упало! Сервер недоступен'),
    ]

    for level, text in test_cases:
        print(f'Ставим в очередь: {level.upper()}...', end=' ')
        try:
            result = send_notify(
                text=text,
                level=level,
                extra={
                    'project': 'vk-sender',
                    'environment': 'test',
                    'mode': 'queue',
                },
                fail_silently=False,
            )
            print('✅ Задача добавлена' if result else '⚠️  Не добавлена')
        except Exception as e:
            print(f'❌ Ошибка: {e}')
        print('-' * 60)

    print('\n💡 Для отправки запустите воркер:')
    print('   python manage.py rqworker')


def run_mocked_queue(user_id: int, token: str):
    """Отправка с замоканной очередью (эмулирует вызов джобы напрямую)."""
    from vk_sender.jobs import send_notification_job

    print('🎭 Режим: МОК ОЧЕРЕДИ (вызов джобы напрямую)\n')

    test_cases = [
        ('info', 'ℹ️ Это тестовое информационное сообщение'),
        ('warning', '⚠️ Внимание: заканчивается место на диске'),
        ('error', '❌ Ошибка при обработке заказа #12345'),
        ('critical', '🚨 КРИТИЧНО: Приложение упало! Сервер недоступен'),
    ]

    for level, text in test_cases:
        print(f'Выполняем джобу: {level.upper()}...', end=' ')
        try:
            result = send_notification_job(
                text=text,
                level=level,
                extra={
                    'project': 'vk-sender',
                    'environment': 'test',
                    'mode': 'mocked',
                },
            )
            print('✅' if result else '⚠️  Не отправлено')
        except Exception as e:
            print(f'❌ Ошибка: {e}')
        print('-' * 60)


def main():
    user_id, token, direct = parse_args()

    print('🚀 Живой тест vk-sender')
    print(f'   Пользователь: {user_id}')
    print(f'   Токен: {token[:10]}...')
    print()

    if direct:
        # Прямая отправка — не нужен Django
        run_direct(user_id, token)
    else:
        # Настраиваем Django для работы с очередью
        setup_django(user_id, token, use_redis=True)

        try:
            run_with_queue(user_id, token)
        except RuntimeError as e:
            # Если Redis недоступен — фолбек на мок
            print(f'\n⚠️  Redis недоступен: {e}')
            print('Переключаюсь на мок-режим...\n')
            run_mocked_queue(user_id, token)

    print('\n🎉 Тестирование завершено!')


if __name__ == '__main__':
    main()
