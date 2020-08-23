from scrapy.http import HtmlResponse, Request
from tjcrawler.crawler.tjcrawler import TJCrawler
import os


def fake_response_from_file(file_name):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    url = "http://www.example.com"

    responses_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(responses_dir, file_name)

    request = Request(url=url)
    file_content = open(file_path, "r").read()

    response = HtmlResponse(
        url=url, request=request, body=file_content, encoding="utf-8"
    )

    return response


def test_spider():
    spider = TJCrawler(process_number="0821901-51.2018.8.12.0001")
    results = spider.extract_movements(fake_response_from_file("movimentacoes.html"))

    movements = [
        {
            "date": "17/07/2020",
            "details": [
                "Guia de Recolhimento Judicial Emitida",
                "Guia nº 001.1489757-12 - Taxa Judiciária - Lei 3.779/09",
            ],
        },
        {
            "date": "30/06/2020",
            "details": ["Expedição de Termo", "Termo de Remessa - Tribunal de Justiça"],
        },
        {
            "date": "30/06/2020",
            "details": ["Remetidos os Autos para ao Tribunal de Justiça"],
        },
        {
            "date": "23/04/2020",
            "details": ["Recebidos os Autos da Procuradoria do Estado"],
        },
        {
            "date": "23/04/2020",
            "details": [
                "Juntada de Petição Intermediária Realizada",
                "Nº Protocolo: WCGR.20.00949824-9  Tipo da Petição: Contrarrazões de Apelação  Data: 23/04/2020 17:00",
            ],
        },
    ]

    assert results == movements
