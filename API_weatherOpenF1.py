# API_weatherOpenF1.py
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


def _data_manipulation(weather_records, id_session):
    inserted = 0
    for each in weather_records:
        props = {
            'id_session':        id_session,
            'date':              each.get('date'),
            'humidity':          each.get('humidity'),
            'wind_speed':        each.get('wind_speed'),
            'air_temperature':   each.get('air_temperature'),
            'rainfall':          each.get('rainfall'),
            'track_temperature': each.get('track_temperature'),
            'pressure':          each.get('pressure'),
            'wind_direction':    each.get('wind_direction'),
        }
        db_insert.inserir_Weather(props)
        inserted += 1
    logger.info('[WEATHER] %s registros processados | id_session=%s', inserted, id_session)


def weather_api(session_key, id_session):
    dados = _api_get(OPENF1_BASE_URL + 'weather', params={'session_key': session_key})
    if dados is None:
        logger.error('[WEATHER] Nenhum dado recebido | session_key=%s', session_key)
        return
    logger.info('[WEATHER] Registros recebidos: %s | session_key=%s', len(dados), session_key)
    _data_manipulation(dados, id_session)