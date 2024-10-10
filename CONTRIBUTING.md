# Contribuindo para o Projeto

Este documento descreve sucintamente o propósito de cada parte do código no projeto.

## Arquivo: `main.py`
### Função `main()`
Verificar se o login já foi feito ou crido, se sim, manda pra `Home.py`, senão chama `show_login_page()`

### Função `show_login_page()`
Monta a pagina de login com os componentes necessários e chama`handle_login() ` ao clicar em logar.

### Função `handle_login()`
Chama a função `login(userName, password)` em `utils.user` para fazer a requisição do login.

## Arquivo: `Home.py`
Monta página da home, como faz uso de muitas outras partes de código vou resumir bem o que cada uma faz através dos imports:
```
from utils.components import *
from utils.functions import *
from data.get_data import get_dashbords_data
from utils.user import logout
from menu.general_dash import GeneralDashPage
from menu.finances import FinancesPage
from menu.reviews import ReviewPage
from menu.operational_performance import OperationalPerformacePage
from menu.show_statement import ShowStatementPage
```

### Em `utils.components`
Nesse arquivo temos os componentes das pagáginas, sempre que algo visual der problema, será aqui. Nessa parte temos alguns timos de funções: 
- `plotFinanceArtist` : funções que criam gráficos com **plot** no começo do nome;
- `buttonDowloadDash` : cria o botão de dawload para um determinado dataframe;
- `filterYearChartFinances` : funções de componentes de filtragem com **filter** no começo do nome;
- `fix_tab_echarts` : há um bug de carregamento do echart com gráficos em outras abas, esse código resolve;
- `hide_sidebar ` : remove a sidebar padrão do streamlit.

### Em `utils.functions`
Nesse arquivo temos algumas lógicas por trás do código que servem para tratar os dados do dataframe: 
- `order` : orderna um dataframe
- `format` : formata os dados
- `translate` : funções auxiliares pra tradução 
- `parse` : conversão de dados
- `sum` : soma de dados
- `to_excel` : retorna um dataframe em excel para dowload

### Em `data.get_data`
Nesse arquivo temos o único código que chama `dbconnect.py` para rodar querys, optei por centralizar tudo aqui.
- `get_dashbords_data` : retorna um dicionário em python com todos os dados das querys que rodou, já aplicando os filtros de estabelecimento e data, se tiver.

### Em `utils.user`
Nesse arquivo temos os códigos referente a login e logou apenas.
- `logout` : usamos para o botão de logout, ele muda o estado da sessão para falso e apaga os dados em cache.

### Em `menu.general_dash`
Nesse arquivo temos o código que constrói a página **Dash Geral**. Lembrando que essa é uma classe que implementa a função `render()` de `page.py`.

### Em `menu.finances`
Nesse arquivo temos o código que constrói a página **Financeiro**. Lembrando que essa é uma classe que implementa a função `render()` de `page.py`.

### Em `menu.reviews`
Nesse arquivo temos o código que constrói a página **Availiação**. Lembrando que essa é uma classe que implementa a função `render()` de `page.py`.

### Em `menu.operational_performance`
Nesse arquivo temos o código que constrói a página **Desempenho Operacional**. Lembrando que essa é uma classe que implementa a função `render()` de `page.py`.

### Em `menu.show_statement`
Nesse arquivo temos o código que constrói a página **Extrato**. Lembrando que essa é uma classe que implementa a função `render()` de `page.py`.
