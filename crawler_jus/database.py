from flask_pymongo import PyMongo
from dynaconf import settings
from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI)
db = client.crawler