from flask import Flask
from dynaconf import FlaskDynaconf


def create_app(**config) -> Flask:
    """
    Creates an application instance to run
    :return: A Flask object
    """
    app = Flask(__name__)

    FlaskDynaconf(
        app, settings_files=["settings.toml"], extensions_list="EXTENSIONS", **config
    )

    return app
