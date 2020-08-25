from flask import Flask
from crawler_jus.ext import configuration


def minimal_app(**config) -> Flask:
    app = Flask(__name__)
    configuration.init_app(app, **config)
    return app


def create_app(**config) -> Flask:
    """
    Creates an application instance to run
    :return: A Flask object
    """
    app = minimal_app(**config)
    configuration.load_extensions(app)
    return app
