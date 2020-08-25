from typing import Dict
from scrapy.crawler import CrawlerProcess
from crawler_jus.crawler.tjms_crawler import TJ2MSCrawler, TJMSCrawler, clean


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


def execute_spider_worker(process_number):
    process = CrawlerProcess(settings={})

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
