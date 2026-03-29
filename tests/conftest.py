import pytest


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Дополнительная настройка БД, если потребуется."""
