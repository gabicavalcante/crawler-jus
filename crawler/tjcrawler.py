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

from utils import clean, clean_proc_value


def save(signal, sender, item, response, spider):
    logger.debug(item)


dispatcher.connect(save, signal=signals.item_passed)


class ProcessData(scrapy.Item):
    classe = scrapy.Field()
    area = scrapy.Field()
    assunto = scrapy.Field()
    distribuicao = scrapy.Field()
    juiz = scrapy.Field()
    valor_acao = scrapy.Field()
    movimentos = scrapy.Field()
    parts = scrapy.Field()


class TJCrawler(scrapy.Spider):
    name = "TJCrawler"
    starting_url = "https://esaj.tjms.jus.br/cpopg5/search.do"
    labels = ["Classe", "Área", "Assunto", "Distribuição", "Juiz", "Valor da ação"]

    def __init__(self, process_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_number = process_number

    def start_requests(self):
        params = {
            "cbPesquisa": "NUMPROC",
            "dadosConsulta.tipoNuProcesso": "UNIFICADO",
            "numeroDigitoAnoUnificado": self.process_number[:15],
            "foroNumeroUnificado": self.process_number[-4:],
            "dadosConsulta.valorConsultaNuUnificado": clean(self.process_number),
        }

        url = f"{self.starting_url}?conversationId=&{urlencode(params)}"
        yield scrapy.Request(url, callback=self.parser_user_data, dont_filter=True)

    def parser_user_data(self, response):
        general_data = self.extract_genaral_data(response)
        parts_data = self.extract_parts(response)
        movements_data = self.extract_movements(response)

        yield ProcessData(
            classe=general_data.get("Classe"),
            area=general_data.get("Área"),
            assunto=general_data.get("Assunto"),
            distribuicao=general_data.get("Distribuição"),
            juiz=general_data.get("Juiz"),
            valor_acao=clean_proc_value(general_data.get("Valor da ação", "")),
            movimentos=movements_data,
            parts=parts_data,
        )

    # TODO: make this more generic
    def extract_movements(self, response):
        results = []
        movements_data = response.xpath(
            "//tbody[contains(@id, 'tabelaTodasMovimentacoes')]//tr"
        )

        for mov in movements_data:
            results.append(
                {
                    "date": clean(mov.xpath("td/text()")[0].get()),
                    "details": "%s/%s"
                    % (
                        (
                            clean(mov.xpath("td/text()")[2].get())
                            or clean(mov.xpath("td")[2].xpath("a/text()").get())
                        ),
                        clean(mov.xpath("td")[2].xpath("span/text()").get()),
                    ),
                }
            )

        return results

    def extract_parts(self, response):
        parts = response.xpath("//table[contains(@id, 'tableTodasPartes')]//tr")

        data_parts = []
        for part in parts:
            first = {
                clean(part.xpath("td[1]/span/text()").get()),
                clean(part.xpath("td[2]/text()").get()),
            }
            data_parts.append(first)

            rows_labels = part.xpath("td[2]/span")
            rows_values = part.xpath("td[2]/text()")[2::2]
            for label, value in zip(rows_labels, rows_values):
                data_parts.append(
                    {clean(label.xpath("text()").get()): clean(value.get()),}
                )

    def extract_genaral_data(self, response):
        general_data = response.xpath("//table[contains(@class, 'secaoFormBody')][1]")

        results: Dict[str, str] = {}
        for label in self.labels:
            if label == "Área":
                results[label] = clean(
                    general_data.xpath(
                        f"//tr[contains(string(), '{label}')]/td[2]/table/tr/td/text()"
                    )[1].get()
                )
            else:
                results[label] = general_data.xpath(
                    f"//tr[contains(string(), '{label}')]/td[2]//span[last()]/text()"
                ).get()
        
        return results


# if __name__ == "__main__":
#     process_number = "0821901-51.2018.8.12.0001"
#     params = {
#         "cbPesquisa": "NUMPROC",
#         "dadosConsulta.tipoNuProcesso": "UNIFICADO",
#         "numeroDigitoAnoUnificado": process_number[:15],
#         "foroNumeroUnificado": process_number[-4:],
#         "dadosConsulta.valorConsultaNuUnificado": clean_proc_number(process_number),
#     }

#     dispatcher.connect(save, signal=signals.item_passed)

#     process = CrawlerProcess(settings={})
#     process.crawl(TJCrawler, proc_data=params)
#     process.start()
