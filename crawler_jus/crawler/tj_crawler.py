from requests_html import HTML

from crawler_jus.crawler.utils import clean_proc_value

from .base import BaseCrawler, ProcessData


class TJ1Crawler(BaseCrawler):
    name = "TJ1_Crawler"

    def parser_user_data(self, html):
        general_data = self.extract_genaral_data(html)
        parts_data = self.extract_parts(html)
        movements_data = self.extract_movements(html)

        return ProcessData(
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


class TJ2Crawler(BaseCrawler):
    name = "TJ2_Crawler"

    def parser_user_data(self, html):
        parts_data = self.extract_parts(html)
        movements_data = self.extract_movements(html)

        return ProcessData(
            process_number=self.process_number,
            level="2",
            movimentos=movements_data,
            parts=parts_data,
        )
