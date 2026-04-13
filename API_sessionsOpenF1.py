import API_weatherOpenF1
import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'

#Filtra e organiza os dados
def data_manipulation(sessions):
    processed_sessions = set()

    for each in sessions:
        session_name    = each['session_name']
        location        = each['location']
        year            = each['year']
        session_key     = (session_name, location, year)

        if session_key in processed_sessions:
            continue

        processed_sessions.add(session_key)
        propriedades = {
            'session type': each['session_type'],
            'session name': each['session_name'],
            'session type': each['session_type'],
            'location':     each['location'],
            'circuit name': each.get('circuit_short_name'),
            'circuit type': each.get('circuit_type'),
            'country name': each.get('country_name'),
            'country_code': each.get('country_code'),
            'meeting_name': each.get('meeting_name'),
            'meeting_oficial_name': each.get('meeting_official_name'),
            'date start':   each['date_start'],
            'date end':     each['date_end'],
            'gmt_offset':   each['gmt_offset'],
            'API key':      each['session_key'],
            'year':         year
        }

        #inserir dados no banco
        db_insert.inserir_Session(propriedades)

        #Realizar a consulta do clima na session
        API_weatherOpenF1.weather_api(each['session_key'])

#Realiza a consulta na api
def sessions_api():

    response = requests.get(f'{url_OpenF1}sessions')
    if response.status_code == 200:
        dados_json = response.json()
        
        return data_manipulation(dados_json)