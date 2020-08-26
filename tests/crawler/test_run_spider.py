from crawler_jus.crawler.run_spider import (
    create_params_1instance,
    create_params_2instance,
)


def teste_create_params_1instance():
    number = "0821901-51.2018.8.12.0001"
    params = create_params_1instance(number)
    assert params == {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": "0821901-51.2018",
        "foroNumeroUnificado": "0001",
        "dadosConsulta.valorConsultaNuUnificado": "08219015120188120001",
    }


def teste_create_params_2instance():
    number = "0821901-51.2018.8.12.0001"
    params = create_params_2instance(number)
    assert params == {
        "cbPesquisa": "NUMPROC",
        "tipoNuProcesso": "UNIFICADO",
        "numeroDigitoAnoUnificado": "0821901-51.2018",
        "foroNumeroUnificado": "0001",
        "dePesquisaNuUnificado": "08219015120188120001",
    }
