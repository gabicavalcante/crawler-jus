import os
import pytest
from crawler_jus.crawler.tj_crawler import TJ1Crawler

from crawler_jus.crawler.run_spider import get_tj_url
from crawler_jus.crawler.error import UnAcceptedValueError
from .expected_process_data import expected
from dynaconf import settings

from requests_html import HTML

process_number = "0821901-51.2018.8.12.0001"
params = {
    "cbPesquisa": "NUMPROC",
    "dadosConsulta.tipoNuProcesso": "UNIFICADO",
    "numeroDigitoAnoUnificado": "0821901-51.2018",
    "foroNumeroUnificado": "0001",
    "dadosConsulta.valorConsultaNuUnificado": "08219015120188120001",
}


@pytest.fixture()
def spider():
    return TJ1Crawler(
        starting_url=settings.MS_FIRST_INSTANCE,
        process_number=process_number,
        params=params,
    )


def fake_response_from_file(file_name):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
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

    return HTML(html=response.body, async_=True)


def test_spider_parts(spider):
    results = spider.extract_parts(fake_response_from_file("parts.html"))
    parts = [
        {"Autora": "Leidi Silva Ormond Galvão"},
        {"Advogada": "Adriana Catelan Skowronski"},
        {"Advogada": "Ana Silvia Pessoa Salgado de Moura"},
        {"Réu": "Estado de Mato Grosso do Sul"},
        {"RepreLeg": "Procuradoria Geral do Estado de Mato Grosso do Sul"},
    ]

    assert results == parts


def test_spider_movements(spider):
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
                "Nº Protocolo: WCGR.20.00949824-9 Tipo da Petição: Contrarrazões de Apelação Data: 23/04/2020 17:00",
            ],
        },
    ]

    assert results == movements


def test_spider_geral(spider):
    results = spider.extract_genaral_data(fake_response_from_file("geral.html"))

    geral = {
        "Classe": "Procedimento Comum Cível",
        "Área": "Cível",
        "Assunto": "Enquadramento",
        "Distribuição": "30/07/2018 às 12:39 - Automática. 3ª Vara de Fazenda Pública e de Registros Públicos - Campo Grande",
        "Juiz": "Zidiel Infantino Coutinho",
        "Valor da ação": "R$ 10.000,00",
    }
    assert results == geral


@pytest.mark.skip
@pytest.mark.parametrize(
    ["url", "expected"],
    [
        (
            "https://esaj.tjms.jus.br/cpopg5/show.do?processo.codigo=01001ZB2W0000&processo.foro=1&processo.numero=0821901-51.2018.8.12.0001&uuidCaptcha=sajcaptcha_d6309efff9e345a0a7697bc05a6929e7",
            expected,
        )
    ],
)
def test_parse(spider, response, expected):
    result = next(spider.parser_user_data(response))
    assert result == expected


@pytest.mark.skip
@pytest.mark.parametrize(
    ["url", "expected"],
    [
        (
            "https://esaj.tjms.jus.br/cpopg5/show.do?processo.codigo=11111ZB2W0000&processo.foro=2&processo.numero=1111111-51.2018.8.12.0001&uuidCaptcha=sajcaptcha_d6309efff9e345a0a7697bc05a6929e7",
            {},
        )
    ],
)
def test_parse(spider, response, expected):
    result = next(spider.parser(response))
    assert result == expected


def test_get_tjcrawler():
    assert get_tj_url("07108025520188020001") == (
        settings.AL_FIRST_INSTANCE,
        settings.AL_SECOND_INSTANCE,
    )
    assert get_tj_url("08219015120188120001") == (
        settings.MS_FIRST_INSTANCE,
        settings.MS_SECOND_INSTANCE,
    )

    with pytest.raises(UnAcceptedValueError) as excinfo:
        assert get_tj_url("07108025520188990001")
