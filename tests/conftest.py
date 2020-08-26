import pytest

from flask import Flask
from crawler_jus.app import create_app
from mock import patch


@pytest.fixture(autouse=True)
def mongo(mongodb):
    class mongo:
        db = mongodb

    return mongo()


@pytest.fixture(autouse=True)
def rabbitmq_broker():
    from dramatiq.brokers.stub import StubBroker
    import dramatiq

    broker = StubBroker()
    broker.emit_after("process_boot")

    dramatiq.set_broker(broker)
    return broker


@pytest.fixture()
def stub_broker(rabbitmq_broker):
    rabbitmq_broker.flush_all()
    return rabbitmq_broker


@pytest.fixture()
def stub_worker(rabbitmq_broker):
    from dramatiq import Worker

    worker = Worker(rabbitmq_broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture(scope="function", autouse=True)
def app(mongo, rabbitmq_broker) -> Flask:
    """
    Provides an instance of our Flask app
    and set dynaconf env to test
    """
    with patch("crawler_jus.ext.db.mongo", mongo):
        app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
        return app
