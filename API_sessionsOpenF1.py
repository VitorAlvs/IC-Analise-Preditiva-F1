import API_weatherOpenF1
import API_DriversOpenF1
import API_sessionresultOpenF1
import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'


#Filtra e organiza os dados
def data_manipulation(sessions):
    processed_sessions = set()
    processed_meetings = set()

    for each in sessions:
        session_name      = each['session_name']
        location          = each['location']
        year              = each['year']
        meeting_name      = each.get('meeting_name')
        country_name      = each.get('country_name')
        meeting_api_key   = each.get('meeting_key')
        meeting_label     = meeting_name if meeting_name else f'meeting_key={meeting_api_key}'
        meeting_check     = (meeting_api_key, country_name, year)
        session_key_check = (session_name, location, year)

        if session_key_check in processed_sessions:
            continue

        processed_sessions.add(session_key_check)

        if meeting_check not in processed_meetings:
            if country_name:
                print(f'[MEETING] Inserindo dados da meeting: {meeting_label} | country={country_name} ({year})')
            else:
                print(f'[MEETING] Inserindo dados da meeting: {meeting_label} ({year})')

            processed_meetings.add(meeting_check)

        print(f'  [SESSION] Inserindo dados da session: {session_name} | {location} | {year}')

        propriedades = {
            'session type':         each['session_type'],
            'session name':         each['session_name'],
            'location':             each['location'],
            'circuit name':         each.get('circuit_short_name'),
            'circuit type':         each.get('circuit_type'),
            'country name':         each.get('country_name'),
            'meeting_name':         each.get('meeting_name'),
            'meeting_oficial_name': each.get('meeting_official_name'),
            'meeting key':          each.get('meeting_key'),
            'date start':           each['date_start'],
            'date end':             each['date_end'],
            'gmt_offset':           each['gmt_offset'],
            'API key':              each['session_key'],
            'year':                 year
        }

        id_session = db_insert.inserir_Session(propriedades)

        if id_session is None:
            print('    [SESSION] Sessao ignorada: meeting nao encontrada para vinculo.')
            continue

        print('    [WEATHER] Inserindo dados de clima da sessao...')
        API_weatherOpenF1.weather_api(each['session_key'])

        print('    [DRIVERS] Inserindo dados de pilotos/equipes da sessao...')
        drivers_map = API_DriversOpenF1.drivers_api(each['session_key'], year)

        print('    [RESULT] Inserindo resultado da sessao...')
        API_sessionresultOpenF1.session_result_api(
            each['session_key'],
            id_session,
            drivers_map
        )


#Realiza a consulta na api
def sessions_api():
    print('[SESSION] Iniciando carga de sessions...')
    response = requests.get(f'{url_OpenF1}sessions')
    if response.status_code == 200:
        dados_json = response.json()
        print(f'[SESSION] Total de sessions retornadas: {len(dados_json)}')
        return data_manipulation(dados_json)

    print(f'[SESSION] Falha na consulta de sessions. Status: {response.status_code}')