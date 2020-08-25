from .process import process_blueprint


def init_app(app):
    app.register_blueprint(process_blueprint)
