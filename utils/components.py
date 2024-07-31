import streamlit as st
from data.get_data import get_geral_information_and_finances
import pandas as pd
import numpy as np
import datetime
from datetime import date
from streamlit_echarts import st_echarts
from utils.functions import *
from decimal import Decimal
import calendar

# resolve o bug de carregamento dos gráficos de echart
def fix_tab_echarts():
    streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 300px;} 
   </style>
    """

    return st.markdown(streamlit_style, unsafe_allow_html=True)

def filterCalendarComponent():
    today = datetime.date.today()

    first_day_of_month = today.replace(day=1)
    last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    d = st.date_input("Filtro de data:", (first_day_of_month, last_day_of_month),
                      format="DD/MM/YYYY")
    return d

def filterEstablishmentComponent(id):
    df = get_geral_information_and_finances(id)
    df_sorted = df.sort_values(by='ESTABELECIMENTO')
    option = st.selectbox("Estabelecimentos:",(df_sorted['ESTABELECIMENTO'].unique()),
            index=None, placeholder="Escolha um")
    return option

def filterProposalComponent():
    option = st.multiselect("Proposta da semana recorrente:",['Aceita','Cancelada','Recusada','Pendente','Checkin Realizado','Checkout Realizado'])
    return option

def filterWeekComponent():
    option = st.selectbox("Agrupar por dia da semana:",['Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo'],
            index=None, placeholder="Escolha um")
    return option

def filterYearChartFinances():
    current_year = date.today().year
    years = list(range(2015, current_year + 1))
    years.insert(0, "Escolha um ano:")
    option = st.selectbox("Escolha um ano:", years, index=years.index(2024))
    return option

def filterReportType(df):
    df = df.sort_values(by='TIPO')
    option = st.selectbox("Tipo de ocorrência:",(df['TIPO'].unique()),
            index=None, placeholder="Escolha um")
    return option

def filterReportArtist(df):
    df = df.sort_values(by='ARTISTA')
    option = st.selectbox("Buscar artista:",(df['ARTISTA'].unique()),
            index=None, placeholder="Selecione um artista")
    return option

def plotDataframe(df, name):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    st.dataframe(df, hide_index=True, use_container_width=True)

def plotLineChart(df, xValue, yValue,name):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    
    if df[xValue].dtype == 'object':
        # Tentar converter os valores para o tipo datetime
        try:
            df_sorted = df.sort_values(by=xValue)
            df_sorted[xValue] = pd.to_datetime(df_sorted[xValue])
            df_sorted[xValue] = df_sorted[xValue].dt.strftime('%d/%m/%Y')
        except ValueError:
            df_sorted = df

    options = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "cross"
            }
        },
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": df_sorted[xValue].tolist(),
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": df_sorted[yValue].tolist(),
                "type": "line",
                "lineStyle": {
                    "color": "#ff6600",  # Cor laranja para a linha
                    "width": 2
                },
                "areaStyle": {
                    "color": "#808080"  # Cor amarela para a área abaixo da linha
                }
            }
        ],
    }
    st_echarts(options=options, height="300px")

def plotPizzaChart(labels, sizes, name):
    chart_key = f"{labels}_{sizes}_{name}_"
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    
    # Preparar os dados para o gráfico
    data = [{"value": size, "name": label} for size, label in zip(sizes, labels)]
    
    options = {
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} ({d}%)" 
        },
        "legend": {
            "orient": "vertical",
            "left": "left",
            "top": "top", 
            "textStyle": {
                "color": "orange"
            }
        },
        "grid": {  # Adicionado para organizar o layout
            "left": "50%", 
            "right": "50%", 
            "containLabel": True
        },
        "series": [
            {
                "name": "Quantidade",
                "type": "pie",
                "radius": "75%",
                "center": ["75%", "45%"],  # Posiciona o gráfico no meio verticalmente
                "data": data,
                "label": {
                    "show": False  # Ocultar os textos nas fatias
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    
    st_echarts(options=options, height="300px", key=chart_key)
    
def plotBarChart(df, xValue, yValue,name):
    chart_key = f"{xValue}_{yValue}_{name}"
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)

    if yValue == 'VALOR_GANHO_BRUTO':
        df = df.rename(columns={'VALOR_GANHO_BRUTO': 'VALOR INVESTIDO'})
        yValue = 'VALOR INVESTIDO'

    if yValue == 'VALOR_BRUTO':
        df = df.rename(columns={'VALOR_BRUTO': 'VALOR INVESTIDO'})
        yValue = 'VALOR INVESTIDO'
    
    if df[xValue].dtype == 'object':
        # Tentar converter os valores para o tipo datetime
        try:
            df_sorted = df.sort_values(by=xValue)
            df_sorted[xValue] = pd.to_datetime(df_sorted[xValue])
            df_sorted[xValue] = df_sorted[xValue].dt.strftime('%d/%m/%Y')
        except ValueError:
            df_sorted = df

    options = {
        "xAxis": {
            "type": "category",
            "data": df_sorted[xValue].tolist(),
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": yValue,
                "data": df_sorted[yValue].tolist(),
                "type": "bar",
                "itemStyle": {
                    "color": "#ff6600"
                },
                "barWidth": "50%"  # Ajuste a largura das colunas aqui
            }
        ],
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "legend": {
            "data": [yValue],
            "textStyle": {
                "color": "#808080"
            }
        }
    }
    
    st_echarts(options=options, height="300px", key=chart_key)

def plotBarChart2(df, xValue, yValue, zValue, name):
    chart_key = f"{xValue}_{yValue}_{zValue}_{name}"
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    
    if df[xValue].dtype == 'object':
        # Tentar converter os valores para o tipo datetime
        try:
            df_sorted = df.sort_values(by=xValue)
            df_sorted[xValue] = pd.to_datetime(df_sorted[xValue])
            df_sorted[xValue] = df_sorted[xValue].dt.strftime('%d/%m/%Y')
        except ValueError:
            df_sorted = df

    options = {
    "xAxis": {
        "type": "category",
        "data": df_sorted[xValue].tolist(),
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "name": "Ticket Médio",
            "data": df_sorted[yValue].tolist(),
            "type": "bar",
            "itemStyle": {"color": "#ff6600"},
            "barWidth": "40%",  # Ajuste a largura das colunas aqui
            "tooltip": {"formatter": "{b}: {c} (Ticket Médio)"}  # Formato da dica de ferramenta
        },
        {
            "name": "Quantidade de Shows",
            "data": df_sorted[zValue].tolist(),
            "type": "bar",
            "itemStyle": {"color": "#ffb131"},
            "barWidth": "0%",  # Ajuste a largura das colunas aqui
            "tooltip": {"formatter": "{b}: {c} (Quantidade de Shows)"}  # Formato da dica de ferramenta
        }
    ],
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "legend": {"data": ["Ticket Médio", "Quantidade de Shows"], "textStyle": {"color": "#808080"}}
    }

    
    st_echarts(options=options, height="300px", key=chart_key)

def plotSideBarChart(df, xValue, yValue1, yValue2, name):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    temp = df.head(15)
    temp = temp.iloc[::-1].reset_index(drop=True)
    options = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "legend": {"textStyle": {"color": "#808080"}},
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "value"
        },
        "yAxis": {
            "type": "category",
            "data": temp[xValue].tolist()
        },
        "series": [
            {
                "name": yValue1,
                "type": "bar",
                "stack": "total",
                "label": {
                    "show": True
                },
                "emphasis": {
                    "focus": "series"
                },
                "data": temp[yValue1].tolist(),
                "itemStyle": {
                    "color": "#ffb131"
                }
            },
            {
                "name": yValue2,
                "type": "bar",
                "stack": "total",
                "label": {
                    "show": True
                },
                "emphasis": {
                    "focus": "series"
                },
                "data": temp[yValue2].tolist(),
                "itemStyle": {
                    "color": "#ff6600"  # Tom de laranja diferente para a segunda série
                }
            }
        ]
    }
    st_echarts(options=options, height="300px")

def plotMapChart(df):
    df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])
    st.map(df)

def plotGeneralFinanceChart(df):
    # Transformando e agrupando valores
    df['VALOR_GANHO_BRUTO'] = df['VALOR_GANHO_BRUTO'].astype(int)
    df_byMonth = df.groupby('MES')['VALOR_GANHO_BRUTO'].sum().reset_index()

    # Plotando gráficos
    plotBarChart(order_and_format_month_dataframe(df_byMonth), 'MES', 'VALOR_GANHO_BRUTO', f'Valor investido por mês em {datetime.date.today().year}')

def plotGeneralFinanceArtist(df):
    financeDash = df.copy()
    financeDash['VALOR_BRUTO'] = financeDash['VALOR_BRUTO'].astype(float)
    grouped_financeDash = financeDash.groupby('ARTISTA').agg(SOMA_VALOR_BRUTO=('VALOR_BRUTO', 'sum'),QUANTIDADE_SHOWS=('VALOR_BRUTO', 'count')).reset_index()
    grouped_financeDash['TICKET_MEDIO'] = (grouped_financeDash['SOMA_VALOR_BRUTO'] / grouped_financeDash['QUANTIDADE_SHOWS']).round(2)
    grouped_financeDash = grouped_financeDash.sort_values(by='QUANTIDADE_SHOWS', ascending=False)
    grouped_financeDash = grouped_financeDash.rename(columns={'TICKET_MEDIO': 'TICKET MÉDIO', 'QUANTIDADE_SHOWS': 'QUANTIDADE DE SHOWS'})

    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>Ticket médio por artista</h5>", unsafe_allow_html=True)

    if grouped_financeDash.empty:
        st.write('')
        st.info('Não há dados de artistas nesse estabelecimento.')
    else:
        st.dataframe(grouped_financeDash[['ARTISTA','TICKET MÉDIO', 'QUANTIDADE DE SHOWS']].sort_values(by='TICKET MÉDIO', ascending=False),
            column_config={
            "TICKET MÉDIO": st.column_config.ProgressColumn(
                "TICKET MÉDIO",
                help="Ticket médio e quantiade de shows de artistas que tocaram na casa",
                format="R$%.2f",
                min_value=0,
                max_value=grouped_financeDash['TICKET MÉDIO'].max(),
            )},hide_index=True, use_container_width=True, height=310)

def printFinanceData(df):
    row2 = st.columns(3)
    tile = row2[0].container(border=True)
    
    # caso dataframe seja vazio
    if df.empty:
        df = pd.DataFrame({'VALOR_BRUTO': [0], 'VALOR_LIQUIDO': [0], 'STATUS_PROPOSTA': ['']})

    # Converte as colunas para Decimal
    df['VALOR_BRUTO'] = df['VALOR_BRUTO'].apply(lambda x: Decimal(x))
    ticket = 0 if df.shape[0] == 0 else  format_brazilian((sum(df['VALOR_BRUTO']) / df.shape[0]).quantize(Decimal('0.00')))
    
    total_brute = format_brazilian(sum(df['VALOR_BRUTO']).quantize(Decimal('0.00')))
    
    tile.markdown(f"<p style='text-align: center;'>Total de Shows</br>{(df.shape[0])}</p>", unsafe_allow_html=True)

    tile = row2[1].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Valor Total</br>R$ {total_brute}</p>", unsafe_allow_html=True)

    tile = row2[2].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Ticket Médio</br>R$ {ticket}</p>", unsafe_allow_html=True)

def filterFinanceStatus(df):
    option = st.selectbox("Status Financeiro:",(df['STATUS_FINANCEIRO'].unique()),
            index=None, placeholder="Escolha um")
    return option

def plotFinanceCharts(df, financeDash):
    # Transformando e agrupando valores
    df['VALOR_GANHO_BRUTO'] = df['VALOR_GANHO_BRUTO'].astype(int)
    financeDash['VALOR_BRUTO'] = financeDash['VALOR_BRUTO'].astype(float)
    grouped_byWek_financeDash = financeDash.groupby('DIA_DA_SEMANA')['VALOR_BRUTO'].sum().reset_index()
    df_byMonth = df.groupby('MES')['VALOR_GANHO_BRUTO'].sum().reset_index()

    # Plotando gráficos
    with st.expander("Valor investido por semana", expanded=False):
        plotBarChart(df, 'NUMERO_SEMANA', 'VALOR_GANHO_BRUTO', 'Valor investido por semana')
    with st.expander("Valor investido por mês", expanded=False):
        plotBarChart(order_and_format_month_dataframe(df_byMonth), 'MES', 'VALOR_GANHO_BRUTO', 'Valor investido por mês')
    with st.expander("Valor médio investido por dia da semana", expanded=False):
        plotBarChart(order_and_format_weekday_dataframe(grouped_byWek_financeDash), 'DIA_DA_SEMANA', 'VALOR_BRUTO', 'Investimento médio por dia da semana')
  
def buttonDowloadDash(df, name):
    button_key = f"_{name}_"
    st.download_button(
    label='Baixar em Excel',
    data=to_excel(df),
    file_name=f"{name}.xlsx",
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    key=button_key
    )

def plotFinanceArtist(financeDash):
    if financeDash.empty:
        st.info('Não há registros existentes nesse estabelecimento.')
    else:
        financeDash['VALOR_BRUTO'] = financeDash['VALOR_BRUTO'].astype(float)
        
        grouped_financeDash = financeDash.groupby('ARTISTA').agg(SOMA_VALOR_BRUTO=('VALOR_BRUTO', 'sum'),QUANTIDADE_SHOWS=('VALOR_BRUTO', 'count')).reset_index()
        grouped_financeDash['TICKET_MEDIO'] = (grouped_financeDash['SOMA_VALOR_BRUTO'] / grouped_financeDash['QUANTIDADE_SHOWS']).round(2)
        grouped_financeDash = grouped_financeDash.sort_values(by='QUANTIDADE_SHOWS', ascending=False)
        col1, col2 = st.columns([4,2])
        with col1:
            plotBarChart2(grouped_financeDash.head(20), 'ARTISTA', 'TICKET_MEDIO', 'QUANTIDADE_SHOWS', 'Ranking de mais shows realizados vs. ticket médio')
        grouped_financeDash = grouped_financeDash.rename(columns={'TICKET_MEDIO': 'TICKET MÉDIO', 'QUANTIDADE_SHOWS': 'QUANTIDADE DE SHOWS'})
        with col2:
            st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>Ticket médio por artista</h5>", unsafe_allow_html=True)
            st.dataframe(grouped_financeDash[['ARTISTA','TICKET MÉDIO', 'QUANTIDADE DE SHOWS']].sort_values(by='TICKET MÉDIO', ascending=False),
                column_config={
                "TICKET MÉDIO": st.column_config.ProgressColumn(
                    "TICKET MÉDIO",
                    help="Ticket médio e quantiade de shows de artistas que tocaram na casa",
                    format="R$%.2f",
                    min_value=0,
                    max_value=grouped_financeDash['TICKET MÉDIO'].max(),
                )},hide_index=True, use_container_width=True, height=310)



