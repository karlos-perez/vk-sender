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

## 2. Подключите приложение
В `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'vk_sender',
    ...
]
```

## 3. Добавьте настройки
```python
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
}
```

## 4. Использование
Основная функция

```python
from vk_sender import send_notification

send_notification(
    text="CRITICAL: Приложение упало! Ошибка 500 на /api/orders/",
    level="critical",  # info | warning | error | critical
    extra={
        "Проект": "crm",
        "Окружение": "production",
        "Пользователь": 456
    }
)
```

## 5. Пример сообщения в VK

```
🚨 CRITICAL #20260101_000001

CRITICAL: Приложение упало! Ошибка 500 на /api/orders/

Проект: crm
Окружение: production
Пользователь: 456
```

## 6. Настройка
|Параметр|Описание
|--|--|
ADMINS|Список администраторов с vk_user_id
VK.TOKEN|Дервисный ключ доступа VK
VK.API_VERSION|Версия API (рекомендуется 5.199)
VK.GROUP_ID*|ID группы для отправки от сообщества
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


## 7. Проверка работы
В подключенном и настроенном django приложении:
```bash
$ python3 test_live.py
```
Или
```bash
$ python3 test_live.py --user <vk_user_id> --token <vk_token>
```

## 8. Дорожная карта
- Очередь для сообщений на основе `django-rq`
- Расширенное форматирование сообщений (vkbottle)

## 9. Требования
- Python ≥ 3.8
- Django ≥ 3.2

## 10. Лицензия
MIT License