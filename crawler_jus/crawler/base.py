from typing import Dict, List
from urllib.parse import urlencode
from requests_html import HTMLSession
from pydantic import BaseModel
from abc import ABC, abstractmethod

from crawler_jus.crawler.utils import clean, clean_general_data, format_proc_number


class Moviments(BaseModel):
    date: str
    details: List[str]


class ProcessData(BaseModel):
    process_number: str
    level: str
    classe: str
    area: str
    assunto: str
    distribuicao: str
    juiz: str
    valor_acao: str
    movimentos: List[Moviments]
    parts: List[Dict[str, str]]


def save(item: ProcessData):
    from crawler_jus.database import db

    collection = db.process

    if item:
        collection.insert_one(item.dict())


class BaseCrawler(ABC):
    labels = ["Classe", "Área", "Assunto", "Distribuição", "Juiz", "Valor da ação"]

    def __init__(self, starting_url, process_number, params, *args, **kwargs):
        self.process_number = format_proc_number(process_number)
        self.params = params
        self.starting_url = starting_url

    def start_requests(self):
        session = HTMLSession()
        url = f"{self.starting_url}?conversationId=&{urlencode(self.params)}"
        response = session.get(url)
        return self.parser(response)

    def parser(self, response):
        not_found_process = (
            "Não existem informações disponíveis para os parâmetros informados"
        )

        if not_found_process in response.text:
            return {}
        else:
            result = self.parser_user_data(response.html)
            save(result)

    @abstractmethod
    def parser_user_data(response):
        pass

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
        dropset: str = "\n\t\r:.\xa0"
        data_parts = []

        parts = html.find("#tableTodasPartes,#tablePartesPrincipais", first=True)

        for part in parts.xpath("//tr"):
            rows = part.find("td")[1].text.split("\n")
            first = {
                clean(part.find("td")[0].text, dropset): clean(rows[0], dropset),
            }
            data_parts.append(first)

            for row in rows[1:]:
                part_type = clean(row.split(":")[0], dropset)
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
