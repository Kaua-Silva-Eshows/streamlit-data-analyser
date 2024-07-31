import pandas as pd
from io import BytesIO
from utils.functions import *
import streamlit as st

# Esconde a sidebar caso de problema no config
def hide_sidebar():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# Função para criar um dicionário com dias da semana
def translate_day(dia):
    dias_da_semana = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
    }
    
    try:
        return dias_da_semana[dia]
    except:
        return dia

# Função para formartar dataframe de finanças
def formatFinancesDataframe(df):
    df['DIA_DA_SEMANA'] = df['DIA_DA_SEMANA'].apply(translate_day)
    df['VALOR_BRUTO'] = 'R$ ' + df['VALOR_BRUTO'].astype(str)
    df['VALOR_LIQUIDO'] = 'R$ ' + df['VALOR_LIQUIDO'].astype(str)
    
    df = df.rename(columns={'STATUS_PROPOSTA': 'STATUS PROPOSTA', 'DATA_INICIO': 'DATA', 'HORARIO_INICIO': 'HORÁRIO', 'DIA_DA_SEMANA': 'DIA DA SEMANA',
                     'VALOR_LIQUIDO': 'VALOR LÍQUIDO', 'VALOR_BRUTO': 'VALOR BRUTO', 'STATUS_FINANCEIRO': 'STATUS FINANCEIRO'})

    return df

# Função para converter o arquivo para excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Função para transformar valores em dinheiro
def format_brazilian(num):
        return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para converter o tempo no formato "Xh Ym Zs" para timedelta
def parse_duration(duration_str):
    try:
        if pd.isna(duration_str):
            return pd.Timedelta(0)  # Retorna uma duração de 0 se o valor for nula

        hours, minutes, seconds = 0, 0, 0
        if 'h' in duration_str:
            hours = int(duration_str.split('h')[0].strip())
            duration_str = duration_str.split('h')[1].strip()
        if 'm' in duration_str:
            minutes = int(duration_str.split('m')[0].strip())
            duration_str = duration_str.split('m')[1].strip()
        if 's' in duration_str:
            seconds = int(duration_str.split('s')[0].strip())

        # Verificando e corrigindo valores fora do intervalo
        if hours > 876000: 
            hours = 99999
        if minutes >= 60:
            minutes = 59
        if seconds >= 60:
            seconds = 59

        return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except:
        return pd.Timadelta(hours=0, minutes=0, seconds=0)

# Função para somar coluna DURACAO e devolver o valor total de horas, minutos e segundos 
def sum_duration_from_dataframe(df):
    # Remover linhas com valores NaN na coluna 'DURACAO'
    df = df.dropna(subset=['DURACAO'])
    
    # Aplicar parse_duration apenas nas linhas restantes
    temp = df['DURACAO'].apply(parse_duration)
    
    if not temp.empty:
        # Calcular a soma da duração
        total_duration = temp.sum()
        
        # Calcular o total de segundos da duração
        total_seconds = total_duration.total_seconds()
        
        # Converter para horas, minutos e segundos
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        return hours, minutes, seconds
    else:
        # Retorna 0 se não houver valores na coluna 'DURACAO'
        return 0, 0, 0

# Função de tradução de horas
def translate_duration(duration):
    if isinstance(duration, pd.Timedelta):
        total_seconds = duration.total_seconds()
        if total_seconds == 1800:  # 30 minutos
            return 'meia hora'
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f'{int(minutes)} minutos'
        elif total_seconds < 86400:  # menos que um dia
            hours = total_seconds // 3600
            return f'{int(hours)} hora' if hours == 1 else f'{int(hours)} horas'
        else:
            days = total_seconds // 86400
            return f'{int(days)} dia' if days == 1 else f'{int(days)} dias'
    return str(duration)

# Função para converter a data com tratamento de exceção
def safe_to_datetime(date_str):
    try:
        return pd.to_datetime(date_str, dayfirst=True)
    except Exception:
        return pd.NaT  # Retorna NaT se houver erro na conversão

# Função para aplicar filtro nos dados da tabela de download de finanças
def apply_filter_in_download_finances_dash(financeDash, establishment, date):
    copy = financeDash
    # aplicando filtros de estabelecimento e data
    copy =  apply_filter_establishment_in_dataframe(copy, establishment)

    if date is not None:
        if len(date) > 1 and date[0] is not None and date[1] is not None:
            startDate = pd.Timestamp(date[0])
            endDate = pd.Timestamp(date[1]) + pd.Timedelta(days=1)
            copy = copy.dropna(subset=['DATA_INICIO'])
            copy = copy[copy['DATA_INICIO'] >= startDate]
            copy = copy[copy['DATA_FIM'] <= endDate]
    
    return copy

# Função para formatar os dados da tabela de download de finanças
def format_download_finances_dash(financeDash):
    copy = financeDash
    
    # Colocando mascara nos valores
    copy['DIA_DA_SEMANA'] = copy['DIA_DA_SEMANA'].apply(translate_day)
    copy['VALOR_BRUTO'] = 'R$ ' + copy['VALOR_BRUTO'].apply(format_brazilian).astype(str)
    copy['DATA_FIM'] = copy['DATA_FIM'].apply(safe_to_datetime)

    # Formatar datas válidas
    copy['DATA_INICIO'] = copy['DATA_INICIO'].apply(lambda x: x.strftime('%d/%m/%Y - %H:%M:%S') if not pd.isnull(x) else None)
    copy['DATA_FIM'] = copy['DATA_FIM'].apply(lambda x: x.strftime('%d/%m/%Y') if not pd.isnull(x) else None)

    # Renomeando e removendo colunas
    financeDash_renamed = copy.rename(columns={'STATUS_PROPOSTA': 'STATUS PROPOSTA', 'DATA_INICIO': 'DATA INÍCIO', 'DATA_FIM': 'DATA FIM','DURACAO' : 'DURAÇÃO','DIA_DA_SEMANA': 'DIA DA SEMANA',
                    'VALOR_BRUTO': 'VALOR BRUTO', 'STATUS_FINANCEIRO': 'STATUS FINANCEIRO'})

    new_order = ['STATUS PROPOSTA','ARTISTA','ESTABELECIMENTO','DATA INÍCIO','DURAÇÃO','DATA FIM','DIA DA SEMANA','VALOR BRUTO','STATUS FINANCEIRO']
    financeDash_renamed = financeDash_renamed[new_order]
    
    return financeDash_renamed

# Função para formatar os dados da tabela de finanças
def format_finances_dash(financeDash):
    copy = financeDash

    # Colocando mascara nos valores
    copy['VALOR_BRUTO'] = 'R$ ' + copy['VALOR_BRUTO'].apply(format_brazilian).astype(str)
    copy['DATA_INICIO'] = copy['DATA_INICIO'].apply(safe_to_datetime)
    copy['DATA_FIM'] = copy['DATA_FIM'].apply(safe_to_datetime)

    # Formatar datas válidas
    copy['DATA_INICIO'] = copy['DATA_INICIO'].apply(lambda x: x.strftime('%d/%m/%Y') if not pd.isnull(x) else None)
    copy['DATA_FIM'] = copy['DATA_FIM'].apply(lambda x: x.strftime('%d/%m/%Y') if not pd.isnull(x) else None)

    # Renomeando e removendo colunas
    financeDash_renamed = copy.rename(columns={'STATUS_PROPOSTA': 'STATUS PROPOSTA', 'DATA_INICIO': 'DATA INÍCIO', 'DATA_FIM': 'DATA FIM','DURACAO' : 'DURAÇÃO','DIA_DA_SEMANA': 'DIA DA SEMANA',
                    'VALOR_BRUTO': 'VALOR BRUTO', 'STATUS_FINANCEIRO': 'STATUS FINANCEIRO'})
    new_order = ['STATUS PROPOSTA','ARTISTA','ESTABELECIMENTO','DATA INÍCIO','DURAÇÃO','DIA DA SEMANA','VALOR BRUTO','STATUS FINANCEIRO']
    financeDash_renamed = financeDash_renamed[new_order]

    return financeDash_renamed

# Função para traduzir e colocar na ordem os meses de um dataframe
def order_and_format_month_dataframe(df):
    if not df.empty:
        # Definindo a ordem dos meses
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

        # Criando um DataFrame com todos os meses
        all_months = pd.DataFrame({'MES': range(1, 13)})
        all_months['MES'] = pd.Categorical(all_months['MES'], categories=range(1, 13), ordered=True)
        all_months['MES'] = all_months['MES'].cat.rename_categories(month_order)

        # Mesclando os dados originais com todos os meses
        df = pd.merge(all_months, df, on='MES', how='left')

        # Ordenar o DataFrame pelo mês(index)
        df = df.sort_index()

        # Zerando os valores null
        df['VALOR_GANHO_BRUTO'] = df['VALOR_GANHO_BRUTO'].fillna(0)

        # Traduzir os meses para português
        df['MES'] = df['MES'].replace({'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'})

    return df

# Função para traduzir e colocar na ordem as semanas de um dataframe
def order_and_format_weekday_dataframe(df):
    # Definindo a ordem dos dias da semana em português
    weekday_order = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    # Criando um DataFrame com todos os dias da semana
    all_weekdays = pd.DataFrame({'DIA_DA_SEMANA': weekday_order})

    # Mesclando os dados originais com todos os dias da semana
    df = pd.merge(all_weekdays, df, on='DIA_DA_SEMANA', how='left')

    # Substituindo valores nulos por 0
    df = df.where(pd.notnull(df), 0)

    # Ordenando o DataFrame pelo índice
    df = df.sort_index()

    return df

# Filtro de estabelecimento dataframes
def apply_filter_establishment_in_dataframe(df, establishment):
    if establishment is not None:
        try:
            df = df[df['ESTABELECIMENTO'] == establishment]
        except:
            return df
    return df

# Filtros de data
def apply_filter_data_in_dataframe(df, date):
    if date is not None:
        if len(date) > 1 and date[0] is not None and date[1] is not None:
            startDate = pd.Timestamp(date[0])
            endDate = pd.Timestamp(date[1] + pd.Timedelta(days=1)) 
            try:
                df = df.dropna(subset=['DATA_AVALIACAO'])
                df = df[df['DATA_AVALIACAO'] >= startDate]
                df = df[df['DATA_AVALIACAO'] <= endDate]
            except:
                try:
                    df = df.dropna(subset=['DATA_INICIO'])
                    df = df[df['DATA_INICIO'] >= startDate]
                    df = df[df['DATA_FIM'] <= endDate]
                    df['DATA_INICIO'] = pd.to_datetime(df['DATA_INICIO'], dayfirst=True)
                    df['DATA_FIM'] = pd.to_datetime(df['DATA_FIM'], dayfirst=True)
                    df['DATA_INICIO'] = df['DATA_INICIO'].dt.strftime('%d/%m/%Y')
                    df['DATA_FIM'] = df['DATA_FIM'].dt.strftime('%d/%m/%Y')
                except:
                    try:
                        df = df.dropna(subset=['DATA'])
                        df = df[pd.to_datetime(df['DATA'], format='%d/%m/%Y') >= startDate]
                        df = df[pd.to_datetime(df['DATA'], format='%d/%m/%Y') <= endDate]
                        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
                    except:
                        return df
            return df
    return df

# Chamas as funções de filtro
def apply_filter_in_dataframe(df, date, establishment):
    df = apply_filter_establishment_in_dataframe(df, establishment)
    df = apply_filter_data_in_dataframe(df, date)
    return df

# agrupa dataframe por semana e cria um campo quantidade para colocar valores
def get_report_artist_by_week(df):
    df['QUANTIDADE'] = df.groupby('SEMANA')['SEMANA'].transform('count')
    df_grouped = df.drop_duplicates(subset=['SEMANA'])
    df_grouped = df_grouped.sort_values(by='QUANTIDADE', ascending=False)
    return df_grouped

# conta o checkin e checkout para a tela de Desempenho Operacional
def transform_show_statement(df):
    # Filtrar apenas as linhas que têm "Checkout Realizado" ou "Checkin Realizado" na coluna "STATUS_PROPOSTA"
    df_filtered = df
    
    # Inicializar colunas para armazenar a contagem
    df_filtered['CHECKIN_REALIZADO'] = 0
    df_filtered['CHECKOUT_REALIZADO'] = 0

    # Atualizar as colunas com base no valor de 'STATUS_PROPOSTA'
    df_filtered.loc[df_filtered['STATUS_PROPOSTA'] == 'Checkin Realizado', 'CHECKIN_REALIZADO'] = 1
    df_filtered.loc[df_filtered['STATUS_PROPOSTA'] == 'Checkout Realizado', 'CHECKOUT_REALIZADO'] = 1

    # Agrupar por 'ARTISTA' e contar o número de ocorrências
    grouped = df_filtered.groupby('ARTISTA').agg({
        'STATUS_PROPOSTA': 'size',  # Conta o número de ocorrências (número de shows)
        'CHECKIN_REALIZADO': 'sum',
        'CHECKOUT_REALIZADO': 'sum'
    }).reset_index()

    grouped['CHECKIN_REALIZADO'] = (((grouped['CHECKIN_REALIZADO'] + grouped['CHECKOUT_REALIZADO'])*100)/grouped['STATUS_PROPOSTA']).map("{:.2f}%".format)
    grouped['CHECKOUT_REALIZADO'] = ((grouped['CHECKOUT_REALIZADO']*100)/grouped['STATUS_PROPOSTA']).map("{:.2f}%".format)
    
    # Renomear as colunas para refletir o que foi pedido
    grouped.rename(columns={
        'STATUS_PROPOSTA': 'NÚMERO DE SHOWS',
        'CHECKIN_REALIZADO': 'PORCENTAGEM DE CHECKIN(%)',
        'CHECKOUT_REALIZADO': 'PORCENTAGEM DE CHECKOUT(%)'
    }, inplace=True)

    return grouped.sort_values(by='NÚMERO DE SHOWS', ascending=False)

# formatando dados do dataframe de artista
def format_artist_ranking(df):
    # Agrupando por nome do artista e calculando a média das notas
    grouped_df = df.groupby('ARTISTA').agg({
        'ESTABELECIMENTO': 'first',
        'DATA_INICIO': 'first',
        'DATA_FIM': 'first',
        'NOTA': ['mean', 'count'],  # Média das notas e contagem de avaliações
        'NUM_SHOWS_ARTISTA': 'first',
        'ESTILO_PRINCIPAL': 'first',
        'EMAIL': 'first',
        'CELULAR': 'first'
    }).reset_index()

    # Flattening the MultiIndex columns
    grouped_df.columns = ['ARTISTA', 'ESTABELECIMENTO', 'DATA_INICIO', 'DATA_FIM', 'NOTA', 'QUANTIDADE_AVALIACOES', 'NUM_SHOWS_ARTISTA' ,'ESTILO_PRINCIPAL', 'EMAIL', 'CELULAR']

    # Renomeando a coluna de média das notas para refletir a agregação
    grouped_df.rename(columns={'NOTA': 'MEDIA_NOTAS'}, inplace=True)

    # Substituir médias nulas por 0
    grouped_df['MEDIA_NOTAS'] = grouped_df['MEDIA_NOTAS'].fillna(0)

    # Formatando MEDIA_NOTAS para ter duas casas decimais
    grouped_df['MEDIA_NOTAS'] = grouped_df['MEDIA_NOTAS'].apply(lambda x: f"{x:.2f}")

    # Ordenar por MEDIA_NOTA em ordem decrescente
    grouped_df = grouped_df.sort_values(by=['MEDIA_NOTAS', 'QUANTIDADE_AVALIACOES','NUM_SHOWS_ARTISTA'], ascending=False)

    # Adicionando estrelas nas notas
    grouped_df['MEDIA_NOTAS'] = '⭐ ' + grouped_df['MEDIA_NOTAS'].astype(str)

    return grouped_df




