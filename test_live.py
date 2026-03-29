"""
Живое тестирование vk-sender.
Отправляет реальные сообщения в VK.
"""

import argparse
import django
import sys

from pathlib import Path
from django.conf import settings

from tests import test_settings

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / 'src'))


parser = argparse.ArgumentParser(description='Тест: Отправка реальных сообщения в VK')
# опционные аргументы
parser.add_argument('--user', help='Идентификатор пользователя VK')
parser.add_argument('--token', help='Токен VK')
# позиционные (необязательные) — nargs="?": 0 или 1 значение
parser.add_argument('vk_user_id', nargs='?', help=argparse.SUPPRESS)
parser.add_argument('vk_token', nargs='?', help=argparse.SUPPRESS)

args = parser.parse_args()

# приоритет: опционные > позиционные
vk_user = args.user if args.user is not None else args.vk_user_id
vk_token = args.token if args.token is not None else args.vk_token


# Настройка Django
def set_config(user_id: int, token: str):
    if not settings.configured:
        if user_id is None or token is None:
            raise ValueError('Необходимо указать VK_ID получателя и VK_TOKEN!')

        settings.configure(
            DEBUG=test_settings.DEBUG,
            DATABASES=test_settings.DATABASES,
            INSTALLED_APPS=test_settings.INSTALLED_APPS,
            USE_TZ=test_settings.USE_TZ,
            TIME_ZONE=test_settings.TIME_ZONE,
            SECRET_KEY=test_settings.SECRET_KEY,
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
            },
        )

    django.setup()


# Теперь можно импортировать
from src import send_notification


def main():
    print('🚀 Запуск живого теста vk-sender...\n')

    test_cases = [
        ('info', 'Это тестовое информационное сообщение из vk-sender'),
        ('warning', 'Внимание: заканчивается место на диске'),
        ('error', 'Ошибка при обработке заказа #12345'),
        ('critical', '🔴 КРИТИЧНО: Приложение упало! Сервер недоступен'),
    ]

    for level, text in test_cases:
        print(f'Отправляем уровень: {level.upper()} ...')
        try:
            success = send_notification(
                text=text,
                level=level,
                extra={'project': 'vk-sender', 'environment': 'local_test', 'test_script': 'test_live.py'},
                fail_silently=False,
            )

            if success:
                print(f'✅ {level.upper()} — успешно отправлено')
            else:
                print(f'⚠️  {level.upper()} — отправка не удалась')

        except Exception as e:
            print(f'❌ {level.upper()} — ошибка: {e}')

        print('-' * 60)

    print('\n🎉 Живое тестирование завершено!')


if __name__ == '__main__':
    set_config(
        user_id=vk_user,
        token=vk_token,
    )
    main()
