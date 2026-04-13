import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'

#Realiza a consulta na api
def weather_api(session_key):

    response = requests.get(f'{url_OpenF1}weather?session_key={session_key}')
    if response.status_code == 200:
        dados_json = response.json()

    