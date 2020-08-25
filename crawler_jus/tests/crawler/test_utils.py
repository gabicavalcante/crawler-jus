from crawler_jus.crawler.utils import clean, clean_proc_value


def test_clean():
    assert clean("\n\t\rAdvog\n\t\rada\n\t\r ") == "Advogada"


def test_clean_process_value():
    assert clean_proc_value("R$  10.000,99") == 10000.99
