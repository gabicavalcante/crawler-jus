# Crawler Processos TJ

Projeto de raspagem de dados de processos dos tribunais de Justiça de Alagoas (TJAL) e do Mato Grosso do Sul (TJMS).
Para a coleta de dados é usado [Scrapy](https://docs.scrapy.org/en/latest/) e Flask para a API. 


## Ambiente 

```
pip install -r requirements-dev.txt
```

## API

- `GET /processo/`

```
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
   5. `02`: identificação do tribunal (02 para AL e 12 para MS).
   6. `0001`: código da comarca


- TJMS: 
  - 1º instancia: https://esaj.tjms.jus.br/cpopg5/search.do
  - 2º instancia: https://esaj.tjms.jus.br/cposg5/search.do

- TJAL 
  - 1º grau - https://www2.tjal.jus.br/cpopg/open.do    
  - 2º grau - https://www2.tjal.jus.br/cposg5/open.do
