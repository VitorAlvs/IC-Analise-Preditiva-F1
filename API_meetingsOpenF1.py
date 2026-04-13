import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'


def meeting_to_properties(each):
    return {
        'circuit name':         each['circuit_short_name'],
        'circuit type':         each['circuit_type'],
        'location':             each['location'],
        'country name':         each['country_name'],
        'country_code':         each['country_code'],
        'meeting_name':         each['meeting_name'],
        'meeting_oficial_name': each['meeting_official_name'],
        'date_start':           each['date_start'],
        'date_end':             each['date_end'],
        'gmt_offset':           each['gmt_offset'],
        'year':                 each['year']
    }

#Filtra e organiza os dados
def data_manipulation(meeting):
    processed_meetings = set()

    for each in meeting:
        meeting_name    = each['meeting_name']
        year            = each['year']
        meeting_key     = (meeting_name, year)

        # Evita duplicidade apenas dentro do mesmo ano
        if meeting_key in processed_meetings:
            continue

        processed_meetings.add(meeting_key)
        propriedades = meeting_to_properties(each)

        #inserir dados no banco
        db_insert.inserir_Meeting(propriedades)


def buscar_meeting_por_ano_pais(year, country_name):
    if not year or not country_name:
        return False

    response = requests.get(
        f'{url_OpenF1}meetings',
        params={'year': year, 'country_name': country_name}
    )
    if response.status_code != 200:
        return False

    meetings = response.json()
    if not meetings:
        return False

    for each in meetings:
        propriedades = meeting_to_properties(each)
        db_insert.inserir_Meeting(propriedades)

    return True
        

#Realiza a consulta na api
def meetings_all():
    
    response = requests.get(f'{url_OpenF1}meetings')
    if response.status_code == 200:
        dados_json = response.json()
        
        return data_manipulation(dados_json)
