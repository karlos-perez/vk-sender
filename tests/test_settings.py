from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEBUG = True
SECRET_KEY = 'django-test-secret-key-for-vk-sender'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = ['django.contrib.contenttypes', 'vk_sender']

VK_SENDER = {
    'ADMINS': [
        {'name': 'Test Admin', 'vk_user_id': 123456789},
        {'name': 'Test Dev', 'vk_user_id': 987654321},
    ],
    'VK': {
        'TOKEN': 'test_token_12345',
        'API_VERSION': '5.199',
        # "GROUP_ID": 237145777,  # если отправлять от группы
    },
    # Настройки Redis для очереди уведомлений
    'RQ_QUEUES': {
        'notifications_send': {  # имя очереди (используется в RQ)
            'HOST': 'localhost',  # хост Redis (или из переменных окружения)
            'PORT': 6379,  # порт Redis
            'DB': 1,  # номер базы данных (изолирует данные от остальных)
            'DEFAULT_TIMEOUT': 60,  # таймаут выполнения задачи в секундах
        },
    },
}

USE_TZ = True
TIME_ZONE = 'UTC'

# Отключаем ненужное для тестов
MIDDLEWARE = []
ROOT_URLCONF = None
TEMPLATES = []
