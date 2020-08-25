import click
from loguru import logger
from crawler_jus.ext.db import mongo
from crawler_jus.crawler.run_spider import execute_spider_worker
from crawler_jus.crawler.tjms_crawler import clean

colletion = mongo.db["process"]


def clean_database():
    """Cleans database"""
    result = colletion.delete_many({})
    logger.info(f"{result.deleted_count} documents deleted.")


def generate():
    pass


def crawler():
    pass


def init_app(app):
    # add a single command
    @app.cli.command()
    def generate_process():
        return generate()

    @app.cli.command()
    def clean_db():
        return clean_database()

    @app.cli.command()
    @click.option("--process", "-p")
    def crawler(process):
        logger.info(f"run crawler: {process}")
        execute_spider_worker(process)

    @app.cli.command()
    @click.option("--process", "-p")
    def get_process(process):
        process_data = colletion.find({"process_number": clean(process, dropset=".-")})
        if not process_data:
            print(f"Process number {process} was not found")
        else:
            print([data for data in process_data])
