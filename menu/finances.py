# menu/finances.py
import streamlit as st
from utils.components import *
from utils.functions import *
from decimal import Decimal

from menu.page import Page

def buildFinances(financeDash, weeklyFinances, id):
    printFinanceData(financeDash)
    container = st.container(border=True)
    with container:
        tab1, tab2 = st.tabs(["Por período", "Por artistas"])
        with tab1:
            plotFinanceCharts(weeklyFinances, financeDash)
        with tab2:
            plotFinanceArtist(financeDash)
        st.divider()
        plotDataframe(format_finances_dash(financeDash.copy()), 'Lista de shows')
    pass

class FinancesPage(Page):
    def render(self):
        buildFinances(self.data['financeDash'].copy(), 
                      self.data['weeklyFinances'].copy(), 
                      self.data['id'])
