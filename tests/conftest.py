import pytest
import warnings

from flask import Flask
from crawler_jus.app import create_app
from mock import patch


@pytest.fixture
def mongo(mongodb):
    class mongo:
        db = mongodb

    return mongo()


@pytest.fixture(scope="function", autouse=True)
def app(mongo) -> Flask:
    """
    Provides an instance of our Flask app
    and set dynaconf env to test
    """
    with patch("crawler_jus.ext.db.mongo", mongo):
        app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
        return app
