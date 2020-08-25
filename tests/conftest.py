import pytest
import warnings

from flask import Flask
from crawler_jus.app import create_app, minimal_app


@pytest.fixture(scope="session")
def min_app() -> Flask:
    app = minimal_app(FORCE_ENV_FOR_DYNACONF="testing")
    return app


@pytest.fixture(scope="session")
def app() -> Flask:
    """
    Provides an instance of our Flask app
    and set dynaconf env to test
    """
    app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
    return app
