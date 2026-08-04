# django-vk-sender

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2%2B-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Лёгкая и удобная Django-батарейка** для отправки уведомлений администраторам в **ВКонтакте**.

Позволяет быстро добавить отправку важных уведомлений (ошибки, предупреждения, критические события) в VK из любого Django-проекта.

## ✨ Возможности

- Простая настройка через `settings.py`
- Отправка уведомлений указанным администраторам
- Поддержка разных уровней важности (`info`, `warning`, `error`, `critical`)
- Красивое форматирование сообщений
- Минимальные зависимости
- Полная совместимость со старыми проектами (Python 3.8 + Django 3.2)

## 🚀 Быстрая установка

### 1. Добавьте пакет в проект

```bash
uv add git+https://github.com/karlos-perez/vk-sender.git@main
```
или
```bash
pip install git+https://github.com/karlos-perez/vk-sender.git@main
```

## 2. Подключение в приложение Django
В `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'vk_sender',
    ...
]

VK_SENDER = {
    "ADMINS": [
        {"name": "Главный админ", "vk_user_id": 123456789},
        {"name": "DevOps", "vk_user_id": 987654321},
    ],

    "VK": {
        "TOKEN": "vk1.a.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "API_VERSION": "5.199",
        "GROUP_ID": 12345678,  # необязательно
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
```

Запуск воркера:

```python
# Постоянный воркер
python manage.py rqworker --queue=notifications_send

# Обработать всё и выйти (для cron)
python manage.py rqworker --burst
```
_* очередь по-умолчанию: vk_sender_

Добавить в _docker-compose.yml_ или предпочтительней в _entrypoint.sh_:

```shell
#!/bin/bash
set -e

# ... миграции, сбор статики ...

# Запускаем воркер в фоне
python manage.py rqworker --queue=notifications_send &

# Запускаем uWSGI
uwsgi --ini .../uwsgi.ini
```

## 3. Использование
Основная функция

```python
from vk_sender import send_notify

send_notify(
    text="CRITICAL: Приложение упало! Ошибка 500 на /api/orders/",
    level="critical",  # info | warning | error | critical
    extra={
        "Проект": "crm",
        "Окружение": "production",
        "Пользователь": 456
    }
)
```

## 4. Пример сообщения в VK

```
🚨 CRITICAL #20260101_000001

CRITICAL: Приложение упало! Ошибка 500 на /api/orders/

Проект: crm
Окружение: production
Пользователь: 456
```

## 5. Настройка
|Параметр|Описание
|--|--|
ADMINS|Список администраторов с vk_user_id
VK.TOKEN|Дервисный ключ доступа VK
VK.API_VERSION|Версия API (рекомендуется 5.199)
VK.GROUP_ID*|ID группы для отправки от сообщества
RQ_QUEUES|Настройки Redis для очереди уведомлений
RQ_QUEUES.notifications_send|Имя очереди (используется в RQ)

* необязательно


> Как получить токен VK?
> 
> Создайте:
> 
> Standalone-приложение в VK → раздел «Настройки» → «Ключи доступа» → отметьте Сообщения.
>
> Или (рекомендуется)
>
> Сообщество в VK → раздел «Управление» → раздел «Дополнительно» → → раздел «Работа с API» → «Ключи доступа» → отметьте Сообщения.


## 6. Проверка работы
В подключенном и настроенном django приложении:
```bash
$ python3 test_live.py
```
Или
```bash
$ python3 test_live.py --user <vk_user_id> --token <vk_token>
```

## 7. Дорожная карта
- Очередь для сообщений на основе `django-rq`
- Расширенное форматирование сообщений (vkbottle)

## 8. Требования
- Python ≥ 3.8
- Django ≥ 3.2

## 9. Лицензия
MIT License