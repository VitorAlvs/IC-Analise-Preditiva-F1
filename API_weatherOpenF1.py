import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'

#Filtra e organiza os dados
def data_manipulation(weather):
    processed_weather = set()

    for each in weather:
        api_session_key     = each['session_key']
        api_meeting_key     = each['meeting_key']
        weather_key         = (api_session_key, api_meeting_key)

        if weather_key in processed_weather:
            continue

        #Consultar id_session no banco
        id_session = db_insert.buscar_SessionID(api_session_key)

        processed_weather.add(weather_key)

        propriedades  = {
            'id_session'          : id_session,  
            'date'                : each['date'],
            'humidity'            : each['humidity'],
            'wind_speed'          : each['wind_speed'],
            'air_temperature'     : each['air_temperature'],
            'rainfall'            : each['rainfall'],
            'track_temperature'   : each['track_temperature'],
            'pressure'            : each['pressure'],
            'wind_direction'      : each['wind_direction']         
        }
        
        db_insert.inserir_Weather(propriedades)

#Realiza a consulta na api
def weather_api(session_key):

    response = requests.get(f'{url_OpenF1}weather?session_key={session_key}')
    if response.status_code == 200:
        dados_json = response.json()
        print(f'      [WEATHER] Registros recebidos: {len(dados_json)} | session_key={session_key}')

        return data_manipulation(dados_json)

    print(f'      [WEATHER] Falha na consulta. Status: {response.status_code} | session_key={session_key}')

    