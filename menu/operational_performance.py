# menu/operational_performance.py
import streamlit as st
from utils.components import *
from utils.functions import *
from decimal import Decimal

from menu.page import Page

def buildOperationalPerformace(operationalPerformace, ByOccurrence, ByWeek, allOperationalPerformaceByOccurrenceAndDate, financeDash):
    tab1, tab2= st.tabs(["Resumos", "Extratos"])
    with tab1:
        container1 = st.container(border=True)
        container2 = st.container(border=True)
        with container1: 
            row1 = st.columns(2)
            with row1[0]:
                plotPizzaChart(ByOccurrence['TIPO'], ByOccurrence['QUANTIDADE'], "Tipos de Ocorrências")
                plotBarChart(ByWeek, 'SEMANA', 'QUANTIDADE', "Quantidade de ocorrêcias por semana")
            with row1[1]:
                st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>Ranking de artistas com mais ocorrências</h5>", unsafe_allow_html=True)
                st.dataframe(operationalPerformace[['RANKING','ARTISTA', 'ESTILO','QUANTIDADE']].reset_index(drop=True), hide_index=True,use_container_width=True, height=735)

        with container2:    
            plotDataframe(transform_show_statement(financeDash), "Quantidade de checkin e checkout por artista")
    
    with tab2:
        # removendo valores e reodernando o dataset
        allOperationalPerformaceByOccurrenceAndDate.drop(columns=['SEMANA'], inplace=True)
        allOperationalPerformaceByOccurrenceAndDate = allOperationalPerformaceByOccurrenceAndDate[['ARTISTA', 'ESTILO','ESTABELECIMENTO','DATA','TIPO']]
        allOperationalPerformaceByOccurrenceAndDate['DATA'] = allOperationalPerformaceByOccurrenceAndDate['DATA'].apply(lambda x: x.strftime('%d/%m/%Y') if not pd.isnull(x) else None)
        
        row1 = st.columns(6)
        with row1[0]:
            type = filterReportType(allOperationalPerformaceByOccurrenceAndDate)
        with row1[1]:
            art = filterReportArtist(allOperationalPerformaceByOccurrenceAndDate)
        with row1[5]:
            st.write('') # alinhar botão
            st.write('') # alinhar botão
            buttonDowloadDash(allOperationalPerformaceByOccurrenceAndDate, "Extrato-de-Ocorrencias")
        container = st.container(border=True)
        with container:
            if type is not None:
                allOperationalPerformaceByOccurrenceAndDate = allOperationalPerformaceByOccurrenceAndDate[allOperationalPerformaceByOccurrenceAndDate['TIPO']==type]
            if art is not None:
                allOperationalPerformaceByOccurrenceAndDate = allOperationalPerformaceByOccurrenceAndDate[allOperationalPerformaceByOccurrenceAndDate['ARTISTA']==art]

            plotDataframe(allOperationalPerformaceByOccurrenceAndDate, "Relatório completo de ocorrências")
    pass

class OperationalPerformacePage(Page):
    def render(self):
        buildOperationalPerformace(self.data['operationalPerformace'].copy(), 
                                   self.data['ByOccurrence'].copy(), 
                                   self.data['ByWeek'].copy(), 
                                   self.data['allOperationalPerformaceByOccurrenceAndDate'].copy(),
                                   self.data['financeDash'].copy())
