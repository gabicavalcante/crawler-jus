from multiprocessing import Process
from typing import Dict

import dramatiq
from scrapy.crawler import CrawlerProcess

from crawler_jus.crawler.tj_crawler import TJ1Crawler, TJ2Crawler
from crawler_jus.crawler.utils import format_proc_number

from .error import UnAcceptedValueError
from dynaconf import settings
from loguru import logger


def get_tj_url(process):
    tj = process[14:16]
    if tj == "12":
        return (settings.MS_FIRST_INSTANCE, settings.MS_SECOND_INSTANCE)
    elif tj == "02":
        return (settings.AL_FIRST_INSTANCE, settings.AL_SECOND_INSTANCE)
    else:
        raise UnAcceptedValueError("Processo pertence a TJ não suportado")


def create_params_1instance(process_number: str) -> Dict[str, str]:
    params = {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dadosConsulta.valorConsultaNuUnificado": format_proc_number(process_number),
    }
    return params


def create_params_2instance(process_number: str) -> Dict[str, str]:
    params = {
        "cbPesquisa": "NUMPROC",
        "tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dePesquisaNuUnificado": format_proc_number(process_number),
    }
    return params


def run(crawler, url, process_number, params):
    c = crawler(url, process_number, params)
    c.start_requests()


def start_crawler_process(crawler, url, process_number, params) -> Process:
    proc = Process(target=run, args=(crawler, url, process_number, params))
    proc.start()
    return proc


@dramatiq.actor
def execute_spider_worker(process_number, subprocess=False):
    url1_instance, url2_instance = get_tj_url(format_proc_number(process_number))
    logger.info("execute_spider_worker %s %s" % (url1_instance, url2_instance))

    if subprocess:
        map(
            lambda x: x.join(),
            [
                start_crawler_process(
                    TJ1Crawler,
                    url1_instance,
                    process_number=process_number,
                    params=create_params_1instance(process_number),
                ),
                start_crawler_process(
                    TJ2Crawler,
                    url2_instance,
                    process_number=process_number,
                    params=create_params_1instance(process_number),
                ),
            ],
        )
    else:
        run(
            TJ1Crawler,
            url1_instance,
            process_number=process_number,
            params=create_params_1instance(process_number),
        ),
        run(
            TJ2Crawler,
            url2_instance,
            process_number=process_number,
            params=create_params_1instance(process_number),
        ),
