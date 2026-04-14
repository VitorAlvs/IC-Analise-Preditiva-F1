import db_insert
import requests

url_OpenF1 = 'https://api.openf1.org/v1/'

#Filtra e organiza os dados
def data_manipulation(drivers, year):
    drivers_map = {}

    for each in drivers:
        driver_number = each.get('driver_number')
        first_name    = each.get('first_name')
        last_name     = each.get('last_name')
        full_name     = each.get('full_name')
        name_acronym  = each.get('name_acronym')

        country_name  = each.get('country_name')

        team_name    = each.get('team_name')
        team_colour  = each.get('team_colour')

        if driver_number is None:
            print('      [DRIVERS] Registro ignorado: driver_number ausente')
            continue

        print(f'      [DRIVERS] Processando driver_number={driver_number} | full_name={full_name}')

        id_country = db_insert.buscar_inserir_Country(country_name)
        print(f'      [DRIVERS] Country mapeado | id_country={id_country}')

        id_driver = db_insert.buscar_inserir_Driver(
            id_country,
            driver_number,
            first_name,
            last_name,
            full_name,
            name_acronym
        )
        print(f'      [DRIVERS] Driver mapeado | id_driver={id_driver}')

        id_team = db_insert.buscar_inserir_Team(team_name, team_colour)
        print(f'      [DRIVERS] Team mapeado | id_team={id_team}')

        if id_driver is None or id_team is None:
            print(f'      [DRIVERS] Nao foi possivel vincular Driver-Team | driver_number={driver_number}')
            continue

        id_driver_team_year = db_insert.buscar_inserir_DriverTeamYear(
            id_driver,
            id_team,
            year
        )

        if id_driver_team_year is None:
            print(f'      [DRIVERS] DriverTeamYear invalido | driver_number={driver_number}')
            continue

        print(f'      [DRIVERS] DriverTeamYear mapeado | id_driver_team_year={id_driver_team_year}')

        drivers_map[driver_number] = {
            'ID_Driver'        : id_driver,
            'ID_Team'          : id_team,
            'ID_DriverTeamYear': id_driver_team_year,
            'full_name'        : full_name,
            'team_name'        : team_name
        }

    return drivers_map

#Realiza a consulta na api
def drivers_api(session_key, year):
    response = requests.get(f'{url_OpenF1}drivers?session_key={session_key}')
    if response.status_code == 200:
        dados_json = response.json()
        print(f'      [DRIVERS] Registros recebidos: {len(dados_json)} | session_key={session_key}')
        return data_manipulation(dados_json, year)

    print(f'      [DRIVERS] Falha na consulta. Status: {response.status_code} | session_key={session_key}')
    return {}