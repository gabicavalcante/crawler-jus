from typing import Dict, Tuple
from urllib.parse import urlencode

import scrapy
from loguru import logger
from scrapy import signals
from scrapy.signalmanager import dispatcher
from requests_html import HTML

from scrapy.crawler import CrawlerProcess


def save(signal, sender, item, response, spider):
    logger.debug(item)


class ProcessData(scrapy.Item):
    level = scrapy.Field()
    classe = scrapy.Field()
    area = scrapy.Field()
    assunto = scrapy.Field()
    distribuicao = scrapy.Field()
    juiz = scrapy.Field()
    valor_acao = scrapy.Field()
    movimentos = scrapy.Field()
    parts = scrapy.Field()


def clean_proc_value(value: str) -> float:
    return float(value[2:].replace(".", "").replace(",", ".").strip())


def clean(value: str, dropset: str = "\n\t\r") -> str:
    dropmap = dict.fromkeys(map(ord, dropset))
    return value.translate(dropmap).strip()


def clean_general_data(value: str) -> Tuple:
    new_str = clean(value)
    label, value = new_str.split(":", maxsplit=1)
    return label.strip(), value.strip()


class TJMSCrawler(scrapy.Spider):
    name = "TJMSCrawler"
    starting_url = "https://esaj.tjms.jus.br/cpopg5/search.do"
    labels = ["Classe", "Área", "Assunto", "Distribuição", "Juiz", "Valor da ação"]

    def __init__(self, process_number, params, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_number = process_number
        self.params = params

    def start_requests(self):
        url = f"{self.starting_url}?conversationId=&{urlencode(self.params)}"
        yield scrapy.Request(url, callback=self.parser_user_data, dont_filter=True)

    def parser_user_data(self, response):
        html = HTML(html=response.body, async_=True)

        general_data = self.extract_genaral_data(html)
        parts_data = self.extract_parts(html)
        movements_data = self.extract_movements(html)

        yield ProcessData(
            level="1",
            classe=general_data.get("Classe"),
            area=general_data.get("Área"),
            assunto=general_data.get("Assunto"),
            distribuicao=general_data.get("Distribuição"),
            juiz=general_data.get("Juiz"),
            valor_acao=clean_proc_value(general_data.get("Valor da ação", "")),
            movimentos=movements_data,
            parts=parts_data,
        )

    def extract_movements(self, html):
        results = []
        movements_data = html.find(
            "#tabelaTodasMovimentacoes,tabelaUltimasMovimentacoes", first=True
        )

        for mov in movements_data.xpath("//tr"):
            date = mov.find("td", first=True).text
            details = mov.find("td")[-1].text.split("\n")

            results.append({"date": date, "details": details})
        return results

    def extract_parts(self, html):
        dropset: str = "\n\t\r:\xa0"
        data_parts = []

        parts = html.find("#tableTodasPartes,#tablePartesPrincipais", first=True)
        for part in parts.xpath("//tr"):
            rows = part.find("td")[1].text.split("\n")
            first = {
                clean(part.find("td")[0].text, dropset): clean(rows[0], dropset),
            }
            data_parts.append(first)

            for row in rows[1:]:
                part_type = clean(row.split(":")[0])
                part_name = clean(row.split(":")[1])

                data_parts.append({part_type: part_name})
        return data_parts

    def extract_genaral_data(self, html):
        general_data = html.xpath("//table[contains(@class, 'secaoFormBody')]")[1]

        results: Dict[str, str] = {}
        for label in self.labels:
            label, value = clean_general_data(
                general_data.xpath(f"//tr[contains(., '{label}')]", first=True).text
            )
            results[label] = value

            if label == "Distribuição":
                following = general_data.xpath(
                    f"//tr[contains(., '{label}')][1]//following::tr"
                )[0].text
                results[label] += ". %s" % following

        return results


class TJ2MSCrawler(TJMSCrawler):
    name = "TJ2MSCrawler"
    starting_url = "https://esaj.tjms.jus.br/cposg5/search.do"

    def parser_user_data(self, response):
        html = HTML(html=response.body, async_=True)

        parts_data = self.extract_parts(html)
        movements_data = self.extract_movements(html)

        yield ProcessData(
            level="2", movimentos=movements_data, parts=parts_data,
        )


if __name__ == "__main__":
    process_number = "0821901-51.2018.8.12.0001"

    dispatcher.connect(save, signal=signals.item_passed)

    params_1_instance = {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dadosConsulta.valorConsultaNuUnificado": clean(process_number, dropset=".-"),
    }

    process = CrawlerProcess(settings={})
    process.crawl(TJMSCrawler, process_number, params_1_instance)

    params_2_instance = {
        "cbPesquisa": "NUMPROC",
        "tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": process_number[:15],
        "foroNumeroUnificado": process_number[-4:],
        "dePesquisaNuUnificado": clean(process_number, dropset=".-"),
    }

    process.crawl(TJ2MSCrawler, process_number, params_2_instance)
    process.start()

