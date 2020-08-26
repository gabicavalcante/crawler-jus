import click
from itertools import chain
from loguru import logger
from crawler_jus.database import db
from crawler_jus.crawler.run_spider import execute_spider_worker
from crawler_jus.crawler.tjms_crawler import clean
from datetime import datetime
from requests_html import HTMLSession

session = HTMLSession()


colletion = db.process


def clean_database():
    """Cleans database"""
    result = db.process.delete_many({})
    logger.info(f"{result.deleted_count} documents deleted.")


def generate_origem_al():
    url = "https://www.trt19.jus.br/portalTRT19/conteudo/135"

    r = session.get(url)
    rows = r.html.find("table tr")[1:]
    for row in rows:
        yield row.find("td")[1].text


def generate_origem_ms():
    url = "https://www.tjms.jus.br/comarcas/comarcas.php"

    r = session.get(url)
    rows = r.html.find("p.texto-titulo-preto")
    for row in rows:
        yield row.text.split("-")[0].strip()


def create_numbers(ano, tr, j=8):
    """
    j:  órgão ou segmento do Poder Judiciário
        – Supremo Tribunal Federal: 1 (um);
        – Conselho Nacional de Justiça: 2 (dois);
        – Superior Tribunal de Justiça: 3 (três);
        - Justiça Federal: 4 (quatro);
        - Justiça do Trabalho: 5 (cinco);
        - Justiça Eleitoral: 6 (seis);
        - Justiça Militar da União: 7 (sete);
        - Justiça dos Estados e do Distrito Federal e Territórios: 8 (oito);
        - Justiça Militar Estadual: 9 (nove).

    tr: tribunal do respectivo segmento do Poder Judiciário
        – STF, CNJ, STJ, TST, TSE, STM = 0
        – CJF e do CSJT = 90
        – JF, TRF = 01 a 05
        – JT, TRT 01 a 24
        – JE, TRE 01 a 27
        – JMU, CJM 01 a 12
        - JE e do DF e Territórios, TJ 01 a 27
        - JME, os TM MG, RS e SP:  13, 21 e 26
    """
    j = 8
    for process in range(0, 9999999):
        for origem in generate_origem_ms():
            value = f"{process}{ano}{j}{tr}{origem}"
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
            if not colletion.find_one({"process_number": clean(number, dropset=".-")}):
                execute_spider_worker.send(args=(number,), delay=5000)


def init_app(app):
    @app.cli.command()
    def clean_db():
        return clean_database()

    @app.cli.command()
    @click.option("--process", "-p", type=str)
    @click.option("--start_year", "-s")
    @click.option("--subprocess", flag_value=True)
    def crawler(process, start_year, subprocess):
        if process:
            logger.info(f"run crawler: {process}")
            if subprocess:
                execute_spider_worker(process, True)
            else:
                execute_spider_worker(process)
        elif start_year:
            crawler_many(start_year)

    @app.cli.command()
    @click.option("--process", "-p")
    def get_process(process):
        process_data = colletion.find({"process_number": clean(process, dropset=".-")})
        if not process_data:
            print(f"Process number {process} was not found")
        else:
            print([data for data in process_data])
