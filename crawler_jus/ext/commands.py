import click
from itertools import chain
from loguru import logger
from crawler_jus.database import db
from crawler_jus.crawler.run_spider import execute_spider_worker
from crawler_jus.crawler.utils import format_proc_number
from datetime import datetime
from requests_html import HTMLSession

session = HTMLSession()


def clean_database():
    """Cleans database"""
    result = db.process.delete_many({})
    logger.info(f"{result.deleted_count} documents deleted.")


def generate_origem_al():
    url = "https://www.trt19.jus.br/portalTRT19/conteudo/135"

    r = session.get(url)

    rows = r.html.find("table tr")[1:]
    for row in rows:
        yield row.find("td")[0].text


def generate_origem_ms():
    url = "https://www.tjms.jus.br/comarcas/comarcas.php"

    r = session.get(url)
    rows = r.html.find("p.texto-titulo-preto")
    for row in rows:
        yield row.text.split("-")[0].strip()


def create_numbers(ano, tr, j=8):
    for process in range(1, 2):
        if tr == "12":
            generate_origin = generate_origem_ms
        else:
            generate_origin = generate_origem_al
        for origem in generate_origin():
            value = f"{process}{ano}{j}{tr}{origem}00"
            digito_verificador = 98 - (int(value) % 97)
            yield f"{process:07}-{digito_verificador:02}.{ano}.{j}.{tr}.{origem}"


def crawler_many(start_year):
    def generate(start_date, end_date):
        for count in range(end_date - start_date + 1):
            yield start_date + count

    end_year = datetime.now().year
    start_year = int(start_year)

    for year in generate(start_year, end_year):
        generate_al = create_numbers(year, "12")
        generate_ms = create_numbers(year, "02")

        for number in chain(generate_al, generate_ms):
            logger.info(number)
            if not db.process.find_one({"process_number": format_proc_number(number)}):
                execute_spider_worker.send(number, True)


def init_app(app):
    @app.cli.command()
    def clean_db():
        return clean_database()

    @app.cli.command()
    @click.option("--process", "-p", type=str)
    @click.option("--start_year", "-s")
    @click.option("--overwrite", "-o", is_flag=True, default=False)
    def crawler(process, start_year, overwrite):
        if process and not overwrite:
            process_data = db.process.find_one(
                {"process_number": format_proc_number(process)}
            )
            if process_data:
                logger.info("process exists")
                return

        if process:
            logger.info(f"run crawler: {process}")
            execute_spider_worker(process)
        elif start_year:
            crawler_many(start_year)

    @app.cli.command()
    @click.option("--process", "-p")
    @click.option("--level", "-l")
    def get_process(process, level):

        if level:
            process_data = db.process.find(
                {"process_number": format_proc_number(process), "level": level}
            )
        else:
            process_data = db.process.find(
                {"process_number": format_proc_number(process)}
            )
        if not process_data:
            print(f"Process number {process} was not found")
        else:
            print([data for data in process_data])
