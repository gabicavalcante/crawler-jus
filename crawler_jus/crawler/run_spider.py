from multiprocessing import Process
from typing import Dict

import dramatiq
from scrapy.crawler import CrawlerProcess

from crawler_jus.crawler.tjal_crawler import TJ2ALCrawler, TJALCrawler
from crawler_jus.crawler.tjms_crawler import TJ2MSCrawler, TJMSCrawler
from crawler_jus.crawler.utils import format_proc_number

from .error import UnAcceptedValueError


def get_tjcrawler(process):
    tj = process[14:16]
    if tj == "12":
        return (TJMSCrawler, TJ2MSCrawler)
    elif tj == "02":
        return (TJALCrawler, TJ2ALCrawler)
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


def crawler_func(crawler, process_number, settings):
    crawler_process = CrawlerProcess(settings)
    crawler_process.crawl(
        crawler,
        process_number=process_number,
        params=create_params_1instance(process_number),
    )
    crawler_process.start()


def start_crawler_process(crawler, process_number) -> Process:
    all_settings = {**{"TELNETCONSOLE_ENABLED": False}}
    proc = Process(target=crawler_func, args=(crawler, process_number, all_settings,))
    proc.start()
    return proc


@dramatiq.actor
def execute_spider_worker(process_number, subprocess=False):
    crawler1, crawler2 = get_tjcrawler(format_proc_number(process_number))

    if subprocess:
        map(
            lambda x: x.join(),
            [
                start_crawler_process(crawler1, process_number=process_number),
                start_crawler_process(crawler2, process_number=process_number),
            ],
        )
    else:
        try:
            crawler_func(crawler1, process_number=process_number, settings={})
            crawler_func(crawler2, process_number=process_number, settings={})
        except Exception:
            import traceback

            return "error", traceback.format_exc()
        else:
            return "ok"
