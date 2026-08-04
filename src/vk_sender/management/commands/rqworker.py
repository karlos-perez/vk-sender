from __future__ import annotations

import logging

from django.core.management.base import BaseCommand
from rq import Worker

from vk_sender.queue import QueueManager


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запускает RQ-воркер для очереди vk_sender'

    def add_arguments(self, parser) -> None:  # noqa: ANN001
        parser.add_argument(
            '--queue',
            type=str,
            default='vk_sender',
            help='Имя очереди (по умолчанию vk_sender)',
        )
        parser.add_argument(
            '--burst',
            action='store_true',
            help='Обработать очередь и выйти (для cron)',
        )

    def handle(self, **options) -> None:
        queue_name = options['queue']
        burst = options['burst']

        # Получаем очередь
        queue = QueueManager.get_instance().get_queue(queue_name)

        # Создаём воркер
        worker = Worker([queue], connection=queue.connection)
        worker.work(burst=burst, with_scheduler=False)

        logger.info(f'Воркер запущен: очередь={queue_name}, burst={burst}')
