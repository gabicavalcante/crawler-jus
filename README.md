![CI](https://github.com/gabicavalcante/crawler-jus/workflows/CI/badge.svg)
[![coverage](https://codecov.io/gh/gabicavalcante/crawler-jus/branch/master/graph/badge.svg)](https://codecov.io/gh/gabicavalcante/crawler-jus)

# Crawler Processos TJ

Projeto de raspagem de dados de processos dos tribunais de Justiça de Alagoas (TJAL) e do Mato Grosso do Sul (TJMS).
Para a coleta de dados é usado [Scrapy](https://docs.scrapy.org/en/latest/) e Flask para a API. 

## Projeto

Os resultados do scraper são armazenados no bando de dados (no projeto foi utilizado Mongo). Caso o processo já exista na base de dados, a API retorna um JSON com o um status de sucesso e com as informação do processo no campo `data`. Caso o número do processo seja inválido, a API retorna `422`, e caso o processo ainda não exista no banco, retornamos o status de `processing`, e na próxima requisição a API retorna o dados atualizado. 

### Rodando a aplicacao

Para rodar a API você pode usar o docker-compose ou instalar as dependências do projeto localmente e rodar usando o script `web.sh`. O docker-compose contém o serviço do mongo, do rabbit e da própria API Flask.

```
$ docker-compose up
```

Agora faça uma requisição `POST /process` passando no corpo o número do processo. 

```bash
curl -X POST -H "Content-Type: application/json" \                                                                
 -d '{"process_numbar":"0821901-51.2018.8.12.0001"}' \
 http://0.0.0.0:5000/process
```

Caso já tenhamos os dados do processo no banco, vamos retornar:

```
- classe
- área
- assunto
- data de distribuição
- juiz
- valor da ação
- partes do processo
- lista das movimentações (data e movimento)
```

Para descobrir o tribunal usamos [o padrão CNJ de numeração de processos juridicos](https://www.cnj.jus.br/programas-e-acoes/numeracao-unica/). [Ato](https://atos.cnj.jus.br/atos/detalhar/atos-normativos?documento=119) com mais detalhes sobre a CNJ.

Um número de processo como `0710802-55.2018.8.02.0001`, tem a seguinte estrutura `NNNNNNN-DD.AAAA.J.TR.OOOO`:

1.  `NNNNNNN`: campo com 7 dígitos, correspondente número do processo (`0710802`).
2.  `DD`: dígito verificador (`55`).
3.  `AAAA`: ano do ajuizamento do processo (`2018`).
4.  `J`: órgão ou segmento do Poder Judiciário (`8`).
5.  `TR`: identificação do tribunal (`02` para MS e `12` para AL).
6.  `OOOO`: código da comarca (`0001`).


### Ambiente local

Instale as dependências necessárias.

```bash
$ pip install -r requirements-dev.txt
```

Você pode usar o server de desenvolvimento do python ou rodar o script `web.sh`.

```bash
$ flask run
# or
$ web.sh
```

O comando `web.sh` vai subir a API na porta `5000`, usando 4 workers.

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

### Commands

Para facilitar a utilização dos recursos da aplicação, você pode usar alguns comandos flask implementados com o `click`:

```bash
$ flask clean-db # limpa o banco 
$ flask crawler -p 0710802-55.2018.8.02.0001  # rodar o crawler para baixar os dados do process 0710802-55.2018.8.02.0001, caso já exista registro o crawler não irá executar
$ flask crawler -p 0710802-55.2018.8.02.0001 -overwrite  # caso exista registro no banco, o crawler vai sobrescrever
$ flask get-process -p 0821901-51.2018.8.12.0001 # retorna todos os dados encontrados no banco para o processo 0821901-51.2018.8.12.0001
$ flask get-process -p 0821901-51.2018.8.12.0001 -l 2 # retorna somente os dados para segunda instância, caso queira da primeira, basta mandar com argumento 1
```
 


#### async e file

Caso você queira baixar os processo em background, é necessário ter o RabbitMQ instalado. No docker-compose fornecido no repositório, você também pode encontrar um serviço para o RabbitMQ. 

Para rodar a geração de número de processos, basta executar:
```
$ flask crawler -s 2018  # o crawler vai gerar números de documentos a partir do ano de 2018
```

Em outro terminal, execute o worker do dramatiq.
```bash
dramatiq crawler_jus.crawler.run_spider
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
- [x] Adicionar validacao do número do processo
- [x] Adicionar identificacão de qual TJ é o processo
- [x] Adicionar comandos CLI para facilitar uso da ferramenta
- [x] Generalizar crawler para AL
- [x] Criar docker-compose
- [x] Adicionar rabbit/celery/redis queue para agendar o crawler
