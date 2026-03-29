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
        # "GROUP_ID": 237145869,  # если отправлять от группы
    },
}

USE_TZ = True
TIME_ZONE = 'UTC'

# Отключаем ненужное для тестов
MIDDLEWARE = []
ROOT_URLCONF = None
TEMPLATES = []
