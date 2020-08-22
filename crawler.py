"""
https://esaj.tjms.jus.br/cpopg5/search.do?

conversationId:
    cbPesquisa: NUMPROC
    dadosConsulta.tipoNuProcesso: UNIFICADO
    numeroDigitoAnoUnificado: 0821901-51.2018
    foroNumeroUnificado: 0001
    dadosConsulta.valorConsultaNuUnificado: 08219015120188120001
    dadosConsulta.valorConsulta:
    uuidCaptcha: sajcaptcha_d6309efff9e345a0a7697bc05a6929e7
    pbEnviar: Pesquisar
"""
from typing import Dict
from urllib.parse import urlencode

import scrapy
from loguru import logger
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from re import sub
from decimal import Decimal


def clean_proc_number(number: str) -> str:
    return number.replace(".", "").replace("-", "")


def clean_proc_value(value: str) -> float:
    return float(value[2:].replace(".", "").replace(",", ".").strip())


def clean_string(s: str):
    return s.replace("\n", "").replace("\t", "").replace("\r", "").strip()


def save(signal, sender, item, response, spider):
    logger.debug(item)


class ProcessData(scrapy.Item):
    classe = scrapy.Field()
    area = scrapy.Field()
    assunto = scrapy.Field()
    distribuicao = scrapy.Field()
    juiz = scrapy.Field()
    valor_acao = scrapy.Field()
    movimentos = scrapy.Field()


class TJCrawler(scrapy.Spider):
    name = "TJCrawler"
    starting_url = "https://esaj.tjms.jus.br/cpopg5/search.do"
    labels = ["Classe", "Área", "Assunto", "Distribuição", "Juiz", "Valor da ação"]

    def __init__(self, proc_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_data = proc_data

    def start_requests(self):
        logger.info(self.starting_url)
        url = f"{self.starting_url}?conversationId=&{urlencode(params)}"
        yield scrapy.Request(url, callback=self.parser_user_data, dont_filter=True)

    def parser_user_data(self, response):
        general_data = response.xpath("//table[contains(@class, 'secaoFormBody')][1]")

        results: Dict[str, str] = {}
        for label in self.labels:
            if label == "Área":
                results[label] = (
                    general_data.xpath(
                        f"//tr[contains(string(), '{label}')]/td[2]/table/tr/td/text()"
                    )[1]
                    .get()
                    .replace("\n", "")
                    .replace("\t", "")
                    .strip()
                )
            else:
                results[label] = general_data.xpath(
                    f"//tr[contains(string(), '{label}')]/td[2]//span[last()]/text()"
                ).get()

        data = []
        movements_data = response.xpath(
            "//tbody[contains(@id, 'tabelaUltimasMovimentacoes')]//tr"
        )

        # TODO: make this more generic
        for mov in movements_data:
            data.append(
                {
                    "date": clean_string(mov.xpath("td/text()")[0].get()),
                    "details": "%s/%s"
                    % (
                        (
                            clean_string(mov.xpath("td/text()")[2].get())
                            or clean_string(mov.xpath("td")[2].xpath("a/text()").get())
                        ),
                        clean_string(mov.xpath("td")[2].xpath("span/text()").get()),
                    ),
                }
            )

        yield ProcessData(
            classe=results.get("Classe"),
            area=results.get("Área"),
            assunto=results.get("Assunto"),
            distribuicao=results.get("Distribuição"),
            juiz=results.get("Juiz"),
            valor_acao=clean_proc_value(results.get("Valor da ação", "")),
            movimentos=data,
        )


if __name__ == "__main__":
    process_number = "0821901-51.2018.8.12.0001"
    params = {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dadosConsulta.valorConsultaNuUnificado": clean_proc_number(process_number),
    }

    dispatcher.connect(save, signal=signals.item_passed)

    process = CrawlerProcess(settings={})
    process.crawl(TJCrawler, proc_data=params)
    process.start()
