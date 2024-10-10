from data.dbconnect import *
from utils.functions import *
import pandas as pd

def get_username(id):
    return GET_USER_NAME(id)
    
def get_geral_information_and_finances(id):
    return GET_PROPOSTAS_BY_ID(id)

# Inicializa os valores de data
def initialize_data(id):

    # Dicionário com dados de entrada
    data = {
        'generalFinances':pd.DataFrame(),
        'financeDash':pd.DataFrame(),
        'averageReviewHouseByArtist':pd.DataFrame(),
        'ByOccurrence':pd.DataFrame(),
        'downloadShowStatement':pd.DataFrame(),
        'showStatement':pd.DataFrame(),
        'weeklyFinances':pd.DataFrame(),
        'artistRanking':pd.DataFrame(),
        'reviewArtistByHouse':pd.DataFrame(),
        'averageReviewArtistByHouse':pd.DataFrame(),
        'reviewHouseByArtist':pd.DataFrame(),
        'operationalPerformace':pd.DataFrame(),
        'ByWeek':pd.DataFrame(),
        'allOperationalPerformaceByOccurrenceAndDate':pd.DataFrame(),
        'commentsartists' : pd.DataFrame(),
        'id':id,
        'filterDate':None, 
        'filterEstablishment':None
    }

    return data

def get_data_GeneralDash(data, id, inputDate=None, inputEstablishment=None):
    generalFinances = apply_filter_in_dataframe(GET_WEEKLY_FINANCES(id), inputDate, inputEstablishment)
    financeDash = apply_filter_in_dataframe(GET_GERAL_INFORMATION_AND_FINANCES(id), inputDate, inputEstablishment)
    averageReviewHouseByArtist = apply_filter_in_dataframe(GET_AVAREGE_REVIEW_HOUSE_BY_ARTIST(id), inputDate, inputEstablishment)
    ByOccurrence = apply_filter_in_dataframe(get_report_by_occurrence(GET_ALL_REPORT_ARTIST_BY_OCCURRENCE_AND_DATE(id).copy()), inputDate, inputEstablishment)
    showStatement = apply_filter_in_dataframe(GET_PROPOSTAS_BY_ID(id), inputDate, inputEstablishment)
    showStatement['DIA_DA_SEMANA'] = showStatement['DIA_DA_SEMANA'].apply(translate_day)
    financeDash['DIA_DA_SEMANA'] = financeDash['DIA_DA_SEMANA'].apply(translate_day)
    
    data['generalFinances'] = generalFinances
    data['financeDash'] = financeDash
    data['averageReviewHouseByArtist'] = averageReviewHouseByArtist
    data['ByOccurrence'] = ByOccurrence
    data['showStatement'] = showStatement
    
    return data

def get_data_Finances(data, id, inputDate=None, inputEstablishment=None):
    weeklyFinances = apply_filter_in_dataframe( GET_WEEKLY_FINANCES(id), inputDate, inputEstablishment)
    
    data['weeklyFinances'] = weeklyFinances

    return data

def get_data_Review(data, id, inputDate=None, inputEstablishment=None):
    artistRanking = apply_filter_in_dataframe(GET_ARTIST_RANKING(id), inputDate, inputEstablishment)
    reviewArtistByHouse = apply_filter_in_dataframe(GET_REVIEW_ARTIST_BY_HOUSE(id), inputDate, inputEstablishment)
    averageReviewArtistByHouse = apply_filter_in_dataframe(GET_AVAREGE_REVIEW_ARTIST_BY_HOUSE(id), inputDate, inputEstablishment)
    reviewHouseByArtist = apply_filter_in_dataframe(GET_REVIEW_HOUSE_BY_ARTIST(id), inputDate, inputEstablishment)
    commentsArtists = apply_filter_in_dataframe(GET_COMMENTS_ARTISTS(id), inputDate, inputEstablishment)
    
    data['artistRanking'] = artistRanking
    data['reviewArtistByHouse'] = reviewArtistByHouse
    data['averageReviewArtistByHouse'] = averageReviewArtistByHouse
    data['reviewHouseByArtist'] = reviewHouseByArtist
    data['commentsArtists'] = commentsArtists
    
    return data

def get_data_OperationalPerformace(data, id, inputDate=None, inputEstablishment=None):
    allOperationalPerformaceByOccurrenceAndDate = apply_filter_in_dataframe(GET_ALL_REPORT_ARTIST_BY_OCCURRENCE_AND_DATE(id), inputDate, inputEstablishment)
    operationalPerformace = apply_filter_in_dataframe(get_report_artist(allOperationalPerformaceByOccurrenceAndDate.copy()), inputDate, inputEstablishment)
    ByWeek = apply_filter_in_dataframe(get_report_artist_by_week(allOperationalPerformaceByOccurrenceAndDate.copy()), inputDate, inputEstablishment)
    
    data['allOperationalPerformaceByOccurrenceAndDate'] = allOperationalPerformaceByOccurrenceAndDate
    data['operationalPerformace'] = operationalPerformace
    data['ByWeek'] = ByWeek
    
    return data

def get_data_ShowStatement(data, id, inputDate=None, inputEstablishment=None):
    downloadShowStatement = GET_PROPOSTAS_BY_ID(id)
    
    data['downloadShowStatement'] = downloadShowStatement
    
    return data



