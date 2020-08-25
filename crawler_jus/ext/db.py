from flask_pymongo import PyMongo
from dynaconf import settings

mongo = PyMongo(uri=settings.MONGO_URI)

def init_app(app):
    mongo.init_app(app)
