# menu/show_statement.py
import streamlit as st
from utils.components import *
from utils.functions import *
from decimal import Decimal

from menu.page import Page

def buildShowStatement(showStatement, downloadShowStatement, establishment, date):
    # pegando valores
    total = showStatement.shape[0]
    total_hours, total_minutes, total_seconds = sum_duration_from_dataframe(showStatement)
    ticket = 0 if total == 0 else  format_brazilian((sum(showStatement['VALOR_BRUTO']) / total).quantize(Decimal('0.00')))
    value = format_brazilian(Decimal(sum(showStatement['VALOR_BRUTO'])).quantize(Decimal('0.00')))

    # formatando showStatement
    showStatement_renamed = format_finances_dash(showStatement)
    downloadShowStatement = format_download_finances_dash(apply_filter_in_download_finances_dash(downloadShowStatement, establishment, date))
    buttonDowloadDash(downloadShowStatement, "Extrato-de-Shows")
    row1 = st.columns(4)

    tile = row1[0].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Total de Shows</br>{total}</p>", unsafe_allow_html=True)

    tile = row1[1].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Total de Horas em Shows</br>{total_hours}h {total_minutes}m {total_seconds}s</p>", unsafe_allow_html=True)

    tile = row1[2].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Valor Transacionado</br>R$ {value}</p>", unsafe_allow_html=True)

    tile = row1[3].container(border=True)
    tile.markdown(f"<p style='text-align: center;'>Ticket Médio</br>R$ {ticket}</p>", unsafe_allow_html=True)
    
    

    container = st.container(border=True)
    with container:
        plotDataframe(showStatement_renamed, "Extrato de propostas e shows")
    pass

class ShowStatementPage(Page):
    def render(self):
        buildShowStatement(self.data['showStatement'].copy(),
                           self.data['downloadShowStatement'].copy(),
                           self.data['filterEstablishment'],
                           self.data['filterDate'])
