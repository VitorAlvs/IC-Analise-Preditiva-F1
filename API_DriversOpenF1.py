# API_DriversOpenF1.py
import logging
import time
import requests
import db_insert
from config import OPENF1_BASE_URL, REQUEST_TIMEOUT, REQUEST_MAX_RETRIES, REQUEST_BACKOFF_BASE

logger = logging.getLogger(__name__)


def _api_get(url, params=None):
    for attempt in range(REQUEST_MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                wait = REQUEST_BACKOFF_BASE ** attempt
                logger.warning('[API] Rate limit. Aguardando %ss.', wait)
                time.sleep(wait)
                continue
            logger.error('[API] Falha HTTP %s | url=%s', response.status_code, url)
            return None
        except requests.exceptions.Timeout:
            logger.error('[API] Timeout | url=%s', url)
        except requests.exceptions.RequestException as e:
            logger.error('[API] Erro: %s', e)
        time.sleep(REQUEST_BACKOFF_BASE ** attempt)
    raise RuntimeError('[API] Falha apos {} tentativas | url={}'.format(REQUEST_MAX_RETRIES, url))


def _data_manipulation(drivers, year):
    drivers_map = {}
    for each in drivers:
        driver_number = each.get('driver_number')
        if driver_number is None:
            logger.warning('[DRIVERS] Registro ignorado: driver_number ausente')
            continue

        full_name    = each.get('full_name')
        first_name   = each.get('first_name')
        last_name    = each.get('last_name')
        name_acronym = each.get('name_acronym')
        team_name    = each.get('team_name')
        team_colour  = each.get('team_colour')

        logger.info('[DRIVERS] Processando driver_number=%s | full_name=%s', driver_number, full_name)

        id_driver = db_insert.buscar_inserir_Driver(
            driver_number, first_name, last_name, full_name, name_acronym
        )
        id_team = db_insert.buscar_inserir_Team(team_name, team_colour)

        if id_driver is None or id_team is None:
            logger.warning('[DRIVERS] Nao foi possivel vincular Driver-Team | driver_number=%s', driver_number)
            continue

        id_driver_team_year = db_insert.buscar_inserir_DriverTeamYear(id_driver, id_team, year)
        if id_driver_team_year is None:
            logger.warning('[DRIVERS] DriverTeamYear invalido | driver_number=%s', driver_number)
            continue

        logger.info('[DRIVERS] DriverTeamYear mapeado | id=%s', id_driver_team_year)
        drivers_map[driver_number] = {
            'ID_Driver':         id_driver,
            'ID_Team':           id_team,
            'ID_DriverTeamYear': id_driver_team_year,
            'full_name':         full_name,
            'team_name':         team_name,
        }
    return drivers_map


def drivers_api(session_key, year):
    dados = _api_get(OPENF1_BASE_URL + 'drivers', params={'session_key': session_key})
    if dados is None:
        logger.error('[DRIVERS] Nenhum dado recebido | session_key=%s', session_key)
        return {}
    logger.info('[DRIVERS] Registros recebidos: %s | session_key=%s', len(dados), session_key)
    return _data_manipulation(dados, year)