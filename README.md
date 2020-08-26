![CI](https://github.com/gabicavalcante/crawler-jus/workflows/CI/badge.svg)
[![coverage](https://codecov.io/gh/gabicavalcante/crawler-jus/branch/master/graph/badge.svg)](https://codecov.io/gh/gabicavalcante/crawler-jus)

# Crawler Processos TJ

Projeto de raspagem de dados de processos dos tribunais de Justiça de Alagoas (TJAL) e do Mato Grosso do Sul (TJMS).
Para a coleta de dados é usado [Scrapy](https://docs.scrapy.org/en/latest/) e Flask para a API.

## Projeto

### rodando a aplicacao

Para rodar a API você pode usar o docker-compose ou instalar as dependências do projeto localmente e rodar usando o script `web.sh`.

#### ambiente local

Esse projeto requer Python 3.7+. Instale as dependências necessárias.

```bash
$ pip install -r requirements-dev.txt
```

Rode o script `web.sh`.

```bash
$ web.sh
```

O comando vai subir a API na porta `5000`, usando 4 workers.

```bash
(venv) ➜  crawler-jus (master) ✗ ./web.sh
[2020-08-23 11:52:02 -0300] [35316] [INFO] Starting gunicorn 20.0.4
[2020-08-23 11:52:02 -0300] [35316] [INFO] Listening at: http://0.0.0.0:5000 (35316)
[2020-08-23 11:52:02 -0300] [35316] [INFO] Using worker: sync
[2020-08-23 11:52:02 -0300] [35318] [INFO] Booting worker with pid: 35318
[2020-08-23 11:52:02 -0300] [35319] [INFO] Booting worker with pid: 35319
[2020-08-23 11:52:02 -0300] [35320] [INFO] Booting worker with pid: 35320
[2020-08-23 11:52:02 -0300] [35321] [INFO] Booting worker with pid: 35321
```

#### docker

#### coletando os dados

Para coletar os dados de um determinado processo, execute:

```
$ run.sh
```

Você também pode executar o spider do scrapy:

```
scrapy runspider crawler/tjcrawler.py -a process_number="0821901-51.2018.8.12.0001"
```

## API

- `GET /processo/`

```json
{
  "number": "0710802-55.2018.8.02.0001"
}
```


#### async
```
dramatiq execute_spider_worker
```

Para descobrir o tribunal usamos [o padrão CNJ de numeração de processos juridicos](https://www.cnj.jus.br/programas-e-acoes/numeracao-unica/). [Ato](https://atos.cnj.jus.br/atos/detalhar/atos-normativos?documento=119) com mais detalhes sobre a CNJ.

Um número de processo como `0710802-55.2018.8.02.0001`, tem a seguinte estrutura `NNNNNNN-DD.AAAA.J.TR.OOOO`:

1.  `NNNNNNN`: campo com 7 dígitos, correspondente número do processo (`0710802`).
2.  `DD`: dígito verificador (`55`).
3.  `AAAA`: ano do ajuizamento do processo (`2018`).
4.  `J`: órgão ou segmento do Poder Judiciário (`8`).
5.  `TR`: identificação do tribunal (`02` para MS e `12` para AL).
6.  `OOOO`: código da comarca (`0001`).

- TJMS:

  - 1º instancia: https://esaj.tjms.jus.br/cpopg5/search.do
  - 2º instancia: https://esaj.tjms.jus.br/cposg5/search.do

- TJAL
  - 1º grau - https://www2.tjal.jus.br/cpopg/open.do
  - 2º grau - https://www2.tjal.jus.br/cposg5/open.do

###

### Dados retornados

```
classe
área
assunto
data de distribuição
juiz
valor da ação
partes do processo
lista das movimentações (data e movimento)
```

### TODO

#### v1

- [x] Crawler do MS
  - [x] Recuperar dados gerais
  - [x] Recuperar partes do processo
  - [x] Recuperar lista das movimentações (data e movimento)
  - [x] Pegar dados completos de partes e movimentacoes
  - [x] Corrigir extracao dos dados de movimentos
- [x] Criar testes
- [x] Armazenar dados do crawler no banco (mongo)
- [x] Conectar a API ao banco

#### v2

- [x] Lidar com processos não encontrados
- [x] Adicionar [dramatic](https://dramatiq.io/guide.html#actors)
- [ ] Adicionar validacao do número do processo
- [ ] Adicionar identificacão de qual TJ é o processo
- [x] Adicionar comandos CLI para facilitar uso da ferramenta
- [ ] Generalizar crawler para AL
- [ ] Criar docker-compose
- [x] Adicionar rabbit/celery/redis queue para agendar o crawler
