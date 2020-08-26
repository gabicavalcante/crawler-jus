from flask import Flask
from dynaconf import FlaskDynaconf
import dramatiq

from dramatiq.brokers.rabbitmq import RabbitmqBroker


def create_app(**config) -> Flask:
    """
    Creates an application instance to run
    :return: A Flask object
    """
    app = Flask(__name__)

    rabbitmq_broker = RabbitmqBroker(host="0.0.0.0")
    dramatiq.set_broker(rabbitmq_broker)

    FlaskDynaconf(
        app, settings_files=["settings.toml"], extensions_list="EXTENSIONS", **config
    )

    return app
