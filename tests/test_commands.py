import mock
import requests
import requests_mock


def test_clean_database(mongodb):
    with mock.patch("crawler_jus.database.db") as mock_mongo:
        from crawler_jus.ext.commands import clean_database

        clean_database()
        assert mock_mongo.process


origin_al = """<table class="table" style="width:400px">
	<thead>
		<tr>
			<th>Código</th>
			<th>Unidade</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td><strong>0001</strong></td>
			<td>1ª VT de Maceió</td>
		</tr>
		<tr>
			<td><strong>0002</strong></td>
			<td>2ª&nbsp;VT de Maceió</td>
		</tr>
	</tbody>
</table>
"""


def test_generate_origem_al():
    with requests_mock.Mocker() as m:
        m.get("https://www.trt19.jus.br/portalTRT19/conteudo/135", text=origin_al)

        from crawler_jus.ext.commands import generate_origem_al

        for code in generate_origem_al():
            assert code in ["0001", "0002"]


origin_ms = """<p class="texto-titulo-preto"><a name="campogrande"></a>0001 - CAMPO GRANDE</p>
<p>(Campo Grande, Anhanduí)</p>

<div class="accordion" style="width:95%;">
    <h3>
        <a href="#">4&ordf; Vara Criminal</a>
    </h3>
    <div>
        Nome: Dr. ALESSANDRO LEITE PEREIRA<br />   
</div>
<br/><br/>

<p><span class="texto-titulo-preto"><a name="corumba"></a>0008 - CORUMB&Aacute;</span></p>
<p>(Corumb&aacute;, Albuquerque, Lad&aacute;rio)</p>
<div class="accordion" style="width:95%;">

    <h3><a href="#">
            Vara de Fazenda P&uacute;blica e Registros P&uacute;blicos<br/></a></h3>

    <div>
        Nome: Dr&ordf;. LUIZA VIEIRA SA DE FIGUEIREDO<br />  
</div>
<br/>

<div class="accordion" style="width:95%;">

<h3><a href="#">
        1&ordf; Vara&nbsp; C&iacute;vel <br/></a></h3>
    <div>
    Nome: Dr. MAURICIO CLEBER MIGLIORANZI SANTOS<br /> Fone: (67) 3907-5982 <br/>
</div>
<br/>
"""


def test_generate_origem_ms():
    with requests_mock.Mocker() as m:
        m.get("https://www.trt19.jus.br/portalTRT19/conteudo/135", text=origin_ms)

        from crawler_jus.ext.commands import generate_origem_al

        for code in generate_origem_al():
            assert code in ["0001", "0002"]
