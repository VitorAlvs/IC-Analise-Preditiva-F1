import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'


def normalize_api_value(value):
    if isinstance(value, (list, tuple)):
        for item in value:
            if item is not None:
                return item
        return None

    return value


#Filtra e organiza os dados
def data_manipulation(results, id_session, drivers_map):
    for each in results:
        driver_number = each.get('driver_number')
        driver_info   = drivers_map.get(driver_number)

        if driver_info is None:
            print(f'      [RESULT] Registro ignorado: driver nao mapeado | driver_number={driver_number}')
            continue

        id_driver_team_year = driver_info['ID_DriverTeamYear']
        position            = each.get('position')
        number_of_laps      = each.get('number_of_laps')
        dnf                 = each.get('dnf')
        dns                 = each.get('dns')
        dsq                 = each.get('dsq')
        duration_value      = normalize_api_value(each.get('duration'))
        gap_to_leader_value = normalize_api_value(each.get('gap_to_leader'))

        if isinstance(each.get('duration'), list) or isinstance(each.get('gap_to_leader'), list):
            print(f'      [RESULT] Valores normalizados | driver_number={driver_number} | duration={duration_value} | gap_to_leader={gap_to_leader_value}')

        if (position is None or number_of_laps is None or dnf is None or dns is None or dsq is None or
            duration_value is None or gap_to_leader_value is None):
            print(f'      [RESULT] Registro ignorado por dados nulos/incompletos | driver_number={driver_number}')
            continue

        id_session_result = db_insert.buscar_inserir_SessionResult(
            id_session         = id_session,
            id_driver_team_year = id_driver_team_year,
            position            = position,
            number_of_laps      = number_of_laps,
            dnf                 = dnf,
            dns                 = dns,
            dsq                 = dsq,
            duration            = str(duration_value),
            gap_to_leader       = str(gap_to_leader_value)
        )

        if id_session_result is not None:
            print(f'      [RESULT] Resultado mapeado | driver_number={driver_number} | id_session_result={id_session_result}')

#Realiza a consulta na api
def session_result_api(session_key, id_session, drivers_map):
    response = requests.get(f'{url_OpenF1}session_result?session_key={session_key}')
    if response.status_code == 200:
        dados_json = response.json()
        print(f'      [RESULT] Registros recebidos: {len(dados_json)} | session_key={session_key}')
        data_manipulation(dados_json, id_session, drivers_map)
        return

    print(f'      [RESULT] Falha na consulta. Status: {response.status_code} | session_key={session_key}')