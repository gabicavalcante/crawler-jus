import dramatiq

from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dynaconf import settings


def create_app(app):
    rabbitmq_broker = RabbitmqBroker(host=settings.RABBIT_HOST)
    dramatiq.set_broker(rabbitmq_broker)
