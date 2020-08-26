import dramatiq

from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dynaconf import settings
from loguru import logger


def init_app(app):
    logger.debug(f"connecting to {settings.RABBIT_HOST}")
    rabbitmq_broker = RabbitmqBroker(host=settings.RABBIT_HOST)
    dramatiq.set_broker(rabbitmq_broker)
