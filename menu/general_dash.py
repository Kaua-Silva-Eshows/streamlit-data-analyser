# menu/general_dash.py
from matplotlib import pyplot as plt
import streamlit as st
from utils.components import *
from utils.functions import *
from decimal import Decimal
import pandas as pd
import streamlit as st
import os
from menu.page import Page

def buildGeneralDash(generalFinances, financeDash, averageReviewHouseByArtist, ByOccurrence, showStatement):

    # pegando valores
    artists = len(pd.unique(showStatement['ARTISTA']))
    stablishment = len(pd.unique(showStatement['ESTABELECIMENTO']))
    total = showStatement.shape[0]
    total_hours, total_minutes, total_seconds = sum_duration_from_dataframe(showStatement)
    ticket = 0 if total == 0 else  format_brazilian((sum(showStatement['VALOR_BRUTO']) / total).quantize(Decimal('0.00')))
    value = format_brazilian(Decimal(sum(showStatement['VALOR_BRUTO'])).quantize(Decimal('0.00')))

    # Printando valores em containers
    row1 = st.columns(6)

    tile = row1[0].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Artistas</br>{artists}</p>", unsafe_allow_html=True)

    tile = row1[1].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Estabelecimentos</br>{stablishment}</p>", unsafe_allow_html=True)

    tile = row1[2].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Total de Shows</br>{total}</p>", unsafe_allow_html=True)

    tile = row1[3].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Horas em Shows</br>{total_hours}h {total_minutes}m {total_seconds}s</p>", unsafe_allow_html=True)

    tile = row1[4].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Valor Transacionado</br>R$ {value}</p>", unsafe_allow_html=True)

    tile = row1[5].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Ticket Médio</br>R$ {ticket}</p>", unsafe_allow_html=True)
    
    container = st.container(border=True)
    with container:
        row2 = st.columns([3,2])
        with row2[0]:
            plotGeneralFinanceChart(generalFinances)
            #plotPizzaChart(pizzaChart['TIPO'], pizzaChart['QUANTIDADE'], "Resumo de ocorrêcias por tipo")
        with row2[1]:
            plotGeneralFinanceArtist(financeDash)
        plotDataframe(averageReviewHouseByArtist, "Satisfação do Estabelecimento")
    pass

class GeneralDashPage(Page):
    def render(self):
        buildGeneralDash(self.data['generalFinances'].copy(), 
                         self.data['financeDash'].copy(), 
                         self.data['averageReviewHouseByArtist'].copy(), 
                         self.data['ByOccurrence'].copy(), 
                         self.data['showStatement'].copy())
