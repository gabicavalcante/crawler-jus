from typing import Dict
from scrapy.crawler import CrawlerProcess
from crawler_jus.crawler.tjms_crawler import TJ2MSCrawler, TJMSCrawler, clean
import dramatiq
from multiprocessing import Process


def create_params_1instance(process_number: str) -> Dict[str, str]:
    params = {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dadosConsulta.valorConsultaNuUnificado": clean(process_number, dropset=".-"),
    }
    return params


def create_params_2instance(process_number: str) -> Dict[str, str]:
    params = {
        "cbPesquisa": "NUMPROC",
        "tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dePesquisaNuUnificado": clean(process_number, dropset=".-"),
    }
    return params


def crawler_func(spider, process_number):
    all_settings = {**{"TELNETCONSOLE_ENABLED": False}}

    crawler_process = CrawlerProcess(all_settings)
    crawler_process.crawl(
        spider,
        process_number=process_number,
        params=create_params_1instance(process_number),
    )
    crawler_process.start()


@dramatiq.actor
def execute_spider_worker(process_number, subprocess=False):

    if subprocess:
        Process(target=crawler_func, args=(TJMSCrawler, process_number)).start()
    else:
        try:
            process = CrawlerProcess(settings={})
            process.crawl(
                TJMSCrawler,
                process_number=process_number,
                params=create_params_1instance(process_number),
            )
            process.crawl(
                TJ2MSCrawler,
                process_number=process_number,
                params=create_params_2instance(process_number),
            )
            process.start()
        except Exception:
            import traceback

            return "error", traceback.format_exc()
        else:
            return "ok"
