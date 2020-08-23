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

Para descobrir o tribunal usamos [o padrão CNJ de numeração de processos juridicos](https://www.cnj.jus.br/programas-e-acoes/numeracao-unica/). 

Um número de processo como `0710802-55.2018.8.02.0001`, tem uma estrutura estrutura composta por:
   1. `0710802-55`: número do processo.
   2. `55`: dígito verificador.
   3. `2018`: ano do ajuizamento do processo. 
   4. `8`: órgão ou segmento do Poder Judiciário.
   5. `02`: identificação do tribunal (02 para MS e 12 para AL).
   6. `0001`: código da comarca


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
  - [ ] **➜** Corrigir extracao dos dados de movimentos
- [ ] Criar testes
- [ ] Armazenar dados do crawler no banco (mongo)
- [ ] Conectar a API ao banco
- [ ] Fazer atualizacao no banco em background caso o processo não exista no banco

#### v2

- [ ] Criar docker-compose
- [ ] Generalizar crawler para AL
- [ ] Adicionar celery/redis queue para agendar o crawler
