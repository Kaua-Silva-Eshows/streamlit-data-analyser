import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime

def get_mysql_connection():
    mysql_config = st.secrets["mysql"]
    # Create MySQL connection
    conn = mysql.connector.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        user=mysql_config['username'],
        password=mysql_config['password']
    )    
    return conn

def execute_query(query):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Obter nomes das colunas
    column_names = [col[0] for col in cursor.description]
    
    # Obter resultados
    result = cursor.fetchall()
    
    cursor.close()
    return result, column_names

def getDfFromQuery(consulta):
    result, column_names = execute_query(consulta)
    return pd.DataFrame(result, columns=column_names)

def convert_date(row):
    try:
        row['DATA_INICIO'] = datetime.strptime(row['DATA_INICIO'], '%d/%m/%y').date()
        row['DATA_FIM'] = datetime.strptime(row['DATA_FIM'], '%d/%m/%y').date()
    except ValueError:
        row['DATA_INICIO'] = None
        row['DATA_FIM'] = None 
    return row

# Gerando dados a partir de um dataframe
def get_report_artist(df):
    df['QUANTIDADE'] = df.groupby('ARTISTA')['ARTISTA'].transform('count')
    df_grouped = df.drop_duplicates(subset=['ARTISTA'])
    df_grouped = df_grouped.sort_values(by='QUANTIDADE', ascending=False)
    df_grouped['RANKING'] = df_grouped['QUANTIDADE'].rank(method='first', ascending=False).astype(int)
    df_grouped = df_grouped.reset_index(drop=True)

    return df_grouped

def get_report_by_occurrence(df):
    df['QUANTIDADE'] = df.groupby(['TIPO'])['ARTISTA'].transform('count')
    df_grouped = df.drop_duplicates(subset=['TIPO'])
    df_grouped = df_grouped.sort_values(by='QUANTIDADE', ascending=False)
    return df_grouped

# QUERIES - colocar em outro arquivo
# Extrato
@st.cache_data
def GET_PROPOSTAS_BY_ID(id):
    df =  getDfFromQuery(f"""
                   SELECT
                    P.ID AS ID_PROPOSTA,
                    CASE 
                        WHEN S.DESCRICAO IS NULL THEN "Cancelada"
                        ELSE S.DESCRICAO
                    END AS STATUS_PROPOSTA,
                    C.NAME AS ESTABELECIMENTO,
                    A.NOME AS ARTISTA,
                    DATA_INICIO AS DATA_INICIO,
                    DATA_FIM AS DATA_FIM,
                    DAYNAME(DATA_INICIO) AS DIA_DA_SEMANA,
                    P.VALOR_BRUTO,
                    SF.DESCRICAO AS STATUS_FINANCEIRO,
                    CONCAT(
                    TIMESTAMPDIFF(HOUR, DATA_INICIO, DATA_FIM), 'h ',
                    TIMESTAMPDIFF(MINUTE, DATA_INICIO, DATA_FIM) % 60, 'm ',
                    TIMESTAMPDIFF(SECOND, DATA_INICIO, DATA_FIM) % 60, 's'
                    ) AS DURACAO

                FROM T_PROPOSTAS P
                INNER JOIN T_COMPANIES C ON (P.FK_CONTRANTE = C.ID)
                INNER JOIN T_ATRACOES A ON (P.FK_CONTRATADO = A.ID)
                LEFT JOIN T_PROPOSTA_STATUS S ON (P.FK_STATUS_PROPOSTA = S.ID)
                LEFT JOIN T_PROPOSTA_STATUS_FINANCEIRO SF ON (P.FK_STATUS_FINANCEIRO = SF.ID)
                INNER JOIN T_GRUPO_USUARIO GU ON C.ID = GU.FK_COMPANY
                        AND GU.STATUS = 1
                            AND GU.FK_PERFIL IN (100,101)

                WHERE 
                        P.DATA_INICIO IS NOT NULL 
                    AND A.ID NOT IN (12166)
                        AND GU.FK_USUARIO = {id}
                    AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)
                    
                GROUP BY P.ID
                ORDER BY P.DATA_INICIO ASC
                        """)
    return df

@st.cache_data
def GET_USER_NAME(id):
    return getDfFromQuery(f"""SELECT 
                            TGU.FK_USUARIO,
                            AU.FULL_NAME
                            FROM T_GRUPO_USUARIO TGU
                            INNER JOIN ADMIN_USERS AU ON TGU.FK_USUARIO = AU.ID
                            WHERE
                                TGU.FK_USUARIO = {id}
                            GROUP BY AU.ID
                          """)

# Avaliações - Avaliações dada pela casa
@st.cache_data
def GET_REVIEW_ARTIST_BY_HOUSE(id):
    df = getDfFromQuery(f"""SELECT
                            A.NOME AS ARTISTA,
                            C.NAME AS ESTABELECIMENTO,
                            GC.GRUPO_CLIENTES AS GRUPO,
                            AV.NOTA,
                            AV.COMENTARIO AS 'COMENTÁRIO',
                            AU.FULL_NAME AS AVALIADOR,
                            AU.LOGIN AS EMAIL_AVALIADOR,
                            P.DATA_INICIO AS 'DATA',
                            AV.LAST_UPDATE AS DATA_AVALIACAO

                            FROM T_AVALIACAO_ATRACOES AV
                            INNER JOIN T_PROPOSTAS P ON (P.ID = AV.FK_PROPOSTA)
                            LEFT JOIN ADMIN_USERS AU ON (AU.ID = AV.LAST_USER)
                            INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
                            INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
                            LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON (GC.ID = C.FK_GRUPO)
                            LEFT JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID

                            WHERE
                            GU.STATUS = 1
                            AND GU.FK_USUARIO = {id}
                            AND A.ID NOT IN (12166)

                            ORDER BY
                            DATA DESC
                        """)
    
    df['NOTA'] = '⭐ ' + df['NOTA'].astype(str)
    return df

# Avaliações - Avaliações da casa
@st.cache_data
def GET_REVIEW_HOUSE_BY_ARTIST(id):
    df = getDfFromQuery(f"""SELECT
                            C.NAME AS ESTABELECIMENTO,
                            GC.GRUPO_CLIENTES AS GRUPO,
                            AC.NOTA,
                            AC.LAST_UPDATE AS DATA,
                            P.DATA_INICIO AS DATA_PROPOSTA,
                            AC.COMENTARIO AS 'COMENTÁRIO'

                            FROM T_AVALIACAO_CASAS AC
                            INNER JOIN T_PROPOSTAS P ON (P.ID = AC.FK_PROPOSTA)
                            LEFT JOIN ADMIN_USERS AU ON (AU.ID = AC.LAST_USER)
                            INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
                            INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
                            LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON (GC.ID = C.FK_GRUPO)
                            LEFT JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID

                            WHERE 
                            GU.STATUS = 1
                            AND GU.FK_USUARIO = {id}
                            AND AC.NOTA > 0
                            AND A.ID NOT IN (12166)
                            GROUP BY AC.ID

                            ORDER BY
                            DATA DESC
                        """)  

    df['NOTA'] = '⭐ ' + df['NOTA'].astype(str)
    return df

# Avaliações - Avaliações de artista
@st.cache_data
def GET_AVAREGE_REVIEW_ARTIST_BY_HOUSE(id):
    df = getDfFromQuery(f"""
                        SELECT
                        A.NOME AS ARTISTA,
                        IFNULL(ROUND(AVG(AV.NOTA), 2),'0') AS 'MÉDIA DE NOTAS',
                        COUNT(DISTINCT AV.ID) AS 'AVALIAÇÕES',
                        COUNT(P.FK_CONTRATADO) AS 'NÚMERO DE SHOWS'

                        FROM T_PROPOSTAS P
                        LEFT JOIN T_AVALIACAO_ATRACOES AV ON (P.ID = AV.FK_PROPOSTA)
                        LEFT JOIN ADMIN_USERS AU ON (AU.ID = AV.LAST_USER)
                        INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
                        INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
                        LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON (GC.ID = C.FK_GRUPO)
                        LEFT JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID

                        WHERE
                        GU.STATUS = 1
                        AND GU.FK_USUARIO = {id}
                        AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)
                        AND A.ID NOT IN (12166)
                        GROUP BY
                        A.ID, A.NOME
                        ORDER BY 'MÉDIA DE NOTAS' DESC, 'AVALIAÇÕES' DESC;
    """)
    df['MÉDIA DE NOTAS'] = '⭐ ' + df['MÉDIA DE NOTAS'].astype(str)
    return df

# Avaliações - Avaliações da casa
@st.cache_data
def GET_AVAREGE_REVIEW_HOUSE_BY_ARTIST(id):
    df = getDfFromQuery(f"""SELECT
                            C.NAME AS ESTABELECIMENTO,
                            IFNULL(ROUND(AVG(AC.NOTA), 2),'0') AS 'MÉDIA DE NOTAS',
                            COUNT(DISTINCT AC.ID) AS 'AVALIAÇÕES',
                            COUNT(P.FK_CONTRANTE) AS 'NÚMERO DE SHOWS'

                            FROM T_PROPOSTAS P
                            LEFT JOIN T_AVALIACAO_CASAS AC ON (P.ID = AC.FK_PROPOSTA)
                            LEFT JOIN ADMIN_USERS AU ON (AU.ID = AC.LAST_USER)
                            INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
                            INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
                            LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON (GC.ID = C.FK_GRUPO)
                            LEFT JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID

                            WHERE 
                            GU.STATUS = 1
                            AND GU.FK_USUARIO = {id}
                            AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)
                            AND A.ID NOT IN (12166)

                            GROUP BY
                            C.ID, C.NAME
                            ORDER BY
                            'MÉDIA NOTAS' DESC, 'AVALIAÇÕES' DESC;
    """)
    df['MÉDIA DE NOTAS'] = '⭐ ' + df['MÉDIA DE NOTAS'].astype(str)
    return df

# Avaliações - Rancking
@st.cache_data
def GET_ARTIST_RANKING(id):
    df =  getDfFromQuery(f"""
SELECT
A.NOME AS ARTISTA,
C.NAME AS ESTABELECIMENTO,
P.DATA_INICIO,
P.DATA_FIM,
AV.NOTA AS NOTA,
 (   SELECT COUNT(P2.FK_CONTRATADO)
         FROM T_PROPOSTAS P2
         WHERE P2.FK_CONTRATADO = P.FK_CONTRATADO AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)
      		AND GU.FK_COMPANY = P2.FK_CONTRANTE
     ) AS NUM_SHOWS_ARTISTA,
EM.DESCRICAO AS ESTILO_PRINCIPAL,
A.EMAIL AS EMAIL,
A.CELULAR AS CELULAR

FROM T_PROPOSTAS P
LEFT JOIN T_AVALIACAO_ATRACOES AV ON (P.ID = AV.FK_PROPOSTA)
LEFT JOIN ADMIN_USERS AU ON (AU.ID = AV.LAST_USER)
INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON (GC.ID = C.FK_GRUPO)
LEFT JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID
LEFT JOIN T_ESTILOS_MUSICAIS EM ON A.FK_ESTILO_PRINCIPAL = EM.ID

WHERE
GU.STATUS = 1
AND GU.FK_USUARIO = {id}
AND A.ID NOT IN (12166)
AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)

ORDER BY NOTA DESC
                        """)
    return df

# Financeiro
@st.cache_data
def GET_GERAL_INFORMATION_AND_FINANCES(id): 
    df =getDfFromQuery(f"""
                        SELECT
                        S.DESCRICAO AS STATUS_PROPOSTA,
                        SF.DESCRICAO AS STATUS_FINANCEIRO,
                        C.NAME AS ESTABELECIMENTO,
                        A.NOME AS ARTISTA,
                        P.DATA_INICIO AS DATA_INICIO,
                        P.DATA_FIM AS DATA_FIM,
                        CONCAT(
                        TIMESTAMPDIFF(HOUR, P.DATA_INICIO, P.DATA_FIM), 'h ',
                        TIMESTAMPDIFF(MINUTE, P.DATA_INICIO, P.DATA_FIM) % 60, 'm ',
                        TIMESTAMPDIFF(SECOND, P.DATA_INICIO, P.DATA_FIM) % 60, 's'
                        ) AS DURACAO,
                        DAYNAME(P.DATA_INICIO) AS DIA_DA_SEMANA,
                        P.VALOR_BRUTO,
                        P.VALOR_LIQUIDO,
                        F.ID AS ID_FECHAMENTO,
                        F.DATA_INICIO AS INICIO_FECHAMENTO,
                        F.DATA_FIM AS FIM_FECHAMENTO

                        FROM T_PROPOSTAS P
                        INNER JOIN T_COMPANIES C ON (P.FK_CONTRANTE = C.ID)
                        INNER JOIN T_ATRACOES A ON (P.FK_CONTRATADO = A.ID)
                        LEFT JOIN T_PROPOSTA_STATUS S ON (P.FK_STATUS_PROPOSTA = S.ID)
                        INNER JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID
                        INNER JOIN T_FECHAMENTOS F ON F.ID = P.FK_FECHAMENTO
                        LEFT JOIN T_PROPOSTA_STATUS_FINANCEIRO SF ON (P.FK_STATUS_FINANCEIRO = SF.ID)

                        WHERE 
                        P.FK_STATUS_PROPOSTA IN (100,101,103,104)
                        AND GU.FK_USUARIO = {id}
                        AND A.ID NOT IN (12166)

                        ORDER BY
                            P.DATA_INICIO ASC
                        """)
    
    return df

# Financeiro
@st.cache_data
def GET_WEEKLY_FINANCES(id):
    return getDfFromQuery(f"""
                        SELECT
                            MONTHNAME(P.DATA_INICIO) AS MES,
                            DATE_ADD(DATE(P.DATA_INICIO), INTERVAL(2-DAYOFWEEK(P.DATA_INICIO)) DAY) AS NUMERO_SEMANA,
                            DATE_FORMAT(DATE_ADD(P.DATA_INICIO, INTERVAL(2-DAYOFWEEK(P.DATA_INICIO)) DAY), '%d-%m-%Y') AS DIA,
                            SUM(P.VALOR_BRUTO) AS VALOR_GANHO_BRUTO,
                            SUM(P.VALOR_LIQUIDO) AS VALOR_GANHO_LIQUIDO,
                            C.NAME AS ESTABELECIMENTO
                        FROM 
                            T_PROPOSTAS P
                            INNER JOIN T_COMPANIES C ON (P.FK_CONTRANTE = C.ID)
                            INNER JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID
                        WHERE 
                            P.FK_STATUS_PROPOSTA IN (100,101,103,104)
                            AND GU.FK_USUARIO = {id}
                            AND YEAR(P.DATA_INICIO) = YEAR(CURDATE())
                        GROUP BY 
                            C.ID, YEAR(P.DATA_INICIO), WEEK(P.DATA_INICIO)
                        ORDER BY
                            YEAR(P.DATA_INICIO), WEEK(P.DATA_INICIO) ASC
                          """)

# Desempenho Operacional
@st.cache_data
def GET_ALL_REPORT_ARTIST_BY_OCCURRENCE_AND_DATE(id):
    df = getDfFromQuery(f"""
                            SELECT
                            A.NOME AS ARTISTA,
                            DATE(OA.DATA_OCORRENCIA) AS DATA,
                            DATE_ADD(DATE(OA.DATA_OCORRENCIA), INTERVAL(2-DAYOFWEEK(OA.DATA_OCORRENCIA)) DAY) AS SEMANA,
                            TIPO.TIPO AS TIPO,
                            EM.DESCRICAO AS ESTILO,
                            C.NAME AS ESTABELECIMENTO
                            
                            FROM 
                            T_OCORRENCIAS_AUTOMATICAS OA
                            LEFT JOIN T_PROPOSTAS P ON P.ID = OA.TABLE_ID AND OA.TABLE_NAME = 'T_PROPOSTAS'
                            LEFT JOIN T_NOTAS_FISCAIS NF ON NF.ID = OA.TABLE_ID AND OA.TABLE_NAME = 'T_NOTAS_FISCAIS' AND NF.TIPO = 'NF_UNICA'
                            LEFT JOIN T_NOTAS_FISCAIS NF2 ON NF2.ID = OA.TABLE_ID AND OA.TABLE_NAME = 'T_NOTAS_FISCAIS' AND (NF2.TIPO = 'NF_SHOW_ANTECIPADO' OR NF2.TIPO = 'NF_SHOW_SOZINHOS')
                            INNER JOIN T_ATRACOES A ON A.ID = OA.FK_ATRACAO
                            INNER JOIN T_TIPOS_OCORRENCIAS TIPO ON TIPO.ID = OA.FK_TIPO_OCORRENCIA
                            LEFT JOIN T_FECHAMENTOS F ON F.ID = NF.FK_FECHAMENTO
                            LEFT JOIN T_PROPOSTAS P2 ON P2.ID = NF2.FK_PROPOSTA
                            LEFT JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE OR C.ID = F.FK_CONTRATANTE OR C.ID = P2.FK_CONTRANTE)
                            LEFT JOIN T_ESTILOS_MUSICAIS EM ON A.FK_ESTILO_PRINCIPAL = EM.ID
                            
                            WHERE 
                            C.ID IN (SELECT GU.FK_COMPANY FROM T_GRUPO_USUARIO GU WHERE GU.FK_USUARIO = {id} AND GU.STATUS = 1)
                            AND C.ID NOT IN (102,343,632,633)
                            AND A.ID NOT IN (12166)
                            AND OA.DATA_OCORRENCIA >= '2024-06-06'
                    """)

    return df

@st.cache_data
def GET_COMMENTS_ARTISTS(id):
    df = getDfFromQuery(f"""
                            SELECT
C.NAME AS ESTABELECIMENTO,
AC.COMENTARIO

FROM T_PROPOSTAS P
LEFT JOIN T_AVALIACAO_CASAS AC ON (P.ID = AC.FK_PROPOSTA)
LEFT JOIN ADMIN_USERS AU ON (AU.ID = AC.LAST_USER)
INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON (GC.ID = C.FK_GRUPO)
LEFT JOIN T_GRUPO_USUARIO GU ON GU.FK_COMPANY = C.ID

WHERE 
GU.STATUS = 1
AND GU.FK_USUARIO = {id}
AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)
AND A.ID NOT IN (12166)
AND AC.COMENTARIO IS NOT NULL AND AC.COMENTARIO <> ''

GROUP BY AC.COMENTARIO
                    """)

    return df
