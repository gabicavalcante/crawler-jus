from requests_html import HTML

from crawler_jus.crawler.utils import clean_proc_value

from .base import BaseCrawler, ProcessData


class TJALCrawler(BaseCrawler):
    name = "AL_1_Crawler"
    starting_url = "https://www2.tjal.jus.br/cpopg/search.do"

    def parser_user_data(self, response):
        html = HTML(html=response.body, async_=True)
        not_found_process = (
            "Não existem informações disponíveis para os parâmetros informados"
        )

        if not_found_process in html.text:
            yield {}
        else:
            general_data = self.extract_genaral_data(html)
            parts_data = self.extract_parts(html)
            movements_data = self.extract_movements(html)

            yield ProcessData(
                process_number=self.process_number,
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


class TJ2ALCrawler(BaseCrawler):
    name = "AL_2_Crawler"
    starting_url = "https://www2.tjal.jus.br/cposg5/search.do"

    def parser_user_data(self, response):
        html = HTML(html=response.body, async_=True)

        parts_data = self.extract_parts(html)
        movements_data = self.extract_movements(html)

        yield ProcessData(
            process_number=self.process_number,
            level="2",
            movimentos=movements_data,
            parts=parts_data,
        )
