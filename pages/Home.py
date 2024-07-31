import streamlit as st
import jwt
from utils.components import *
from utils.functions import *
from data.get_data import initialize_data, get_data_GeneralDash, get_data_Finances, get_data_Review, get_data_OperationalPerformace, get_data_ShowStatement
from utils.user import logout

# modularização das páginas
from menu.general_dash import GeneralDashPage
from menu.finances import FinancesPage
from menu.reviews import ReviewPage
from menu.operational_performance import OperationalPerformacePage
from menu.show_statement import ShowStatementPage

def render():
    user_id = st.session_state['user_data']["data"]["user_id"]
    user_name = st.session_state['user_data']["data"]['full_name']

    # Header
    col1, col2, col3 = st.columns([9, 0.7, 1])

    # Caso não ache o ID de usuário
    if user_name is None:
        col1.error('ID de usuário não encontrado')
    else:
        col1.write(f"## Olá, {user_name}")
    col2.image("./assets/imgs/eshows100x100.png")

    col3.write('')  # serve pra alinhar o botão
    if col3.button("Logout"):
        logout()
        st.switch_page("main.py")

    # Nav
    st.divider()
    col4, empty, col5, col6 = st.columns([1, 1, 3, 2])
    with col4:
        inputDate = filterCalendarComponent()
    col5.markdown("<h3 style='text-align: center;'>Relatórios do Estabelecimento</h3>", unsafe_allow_html=True)
    with col6:
        inputEstablishment = filterEstablishmentComponent(user_id)

    data = initialize_data(user_id)
    # Body
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["DASH GERAL", "FINANCEIRO", "AVALIAÇÕES", "DESEMPENHO OPERACIONAL", "EXTRATO DE SHOWS"])
    with tab1:
        try:
            data = get_data_GeneralDash(data, user_id, inputDate, inputEstablishment)
            page = GeneralDashPage(data)
            page.render()
        except Exception as e:
            st.error(f'Não foi possível carregar a página. Erro: {e}')
    with tab2:
        try:
            data = get_data_Finances(data, user_id, inputDate, inputEstablishment)
            page = FinancesPage(data)
            page.render()
        except Exception as e:
            st.error(f'Não foi possível carregar a página. Erro: {e}')
    with tab3:
        try:
            data = get_data_Review(data, user_id, inputDate, inputEstablishment)
            page = ReviewPage(data)
            page.render()
        except Exception as e:
            st.error(f'Não foi possível carregar a página. Erro: {e}')
    with tab4:
        try:
            data = get_data_OperationalPerformace(data, user_id, inputDate, inputEstablishment)
            page = OperationalPerformacePage(data)
            page.render()
        except Exception as e:
            st.error(f'Não foi possível carregar a página. Erro: {e}')
    with tab5:
        try:
            data = get_data_ShowStatement(data, user_id, inputDate, inputEstablishment)
            page = ShowStatementPage(data)
            page.render()
        except Exception as e:
            st.error(f'Não foi possível carregar a página. Erro: {e}')

if __name__ == "__main__":
    if 'jwt_token' not in st.session_state:
        st.switch_page("main.py")

    st.set_page_config(
        page_title="Relatórios Eshows",
        page_icon="./assets/imgs/eshows-logo100x100.png",
        layout="wide",
)

    hide_sidebar()
    fix_tab_echarts()

    if 'user_data' in st.session_state:
        render()
    else:
        st.switch_page("main.py")
