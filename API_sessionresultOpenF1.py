# API_sessionresultOpenF1.py
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


def _normalize_phase_value(value):
    """Qualifying retorna lista [Q1, Q2, Q3]. Usa o ultimo valor nao-nulo."""
    if isinstance(value, (list, tuple)):
        for item in reversed(value):
            if item is not None:
                return item
        return None
    return value


def _format_seconds(value):
    if value is None:
        return None
    try:
        return '{:.3f}'.format(float(value))
    except (TypeError, ValueError):
        return str(value)


def _data_manipulation(results, id_session, drivers_map):
    for each in results:
        driver_number = each.get('driver_number')
        driver_info   = drivers_map.get(driver_number)

        if driver_info is None:
            logger.warning('[RESULT] Driver nao mapeado | driver_number=%s', driver_number)
            continue

        id_driver_team_year = driver_info['ID_DriverTeamYear']
        position       = each.get('position')
        number_of_laps = each.get('number_of_laps')
        dnf = each.get('dnf')
        dns = each.get('dns')
        dsq = each.get('dsq')
        raw_duration        = each.get('duration')
        raw_gap_to_leader   = each.get('gap_to_leader')
        duration_value      = _normalize_phase_value(raw_duration)
        gap_to_leader_value = _normalize_phase_value(raw_gap_to_leader)

        if isinstance(raw_duration, list) or isinstance(raw_gap_to_leader, list):
            logger.info('[RESULT] Valores normalizados | driver_number=%s', driver_number)

        if any(v is None for v in [position, number_of_laps, dnf, dns, dsq,
                                    duration_value, gap_to_leader_value]):
            logger.warning('[RESULT] Dados incompletos, ignorando | driver_number=%s', driver_number)
            continue

        id_result = db_insert.buscar_inserir_SessionResult(
            id_session=id_session,
            id_driver_team_year=id_driver_team_year,
            position=position,
            number_of_laps=number_of_laps,
            dnf=dnf, dns=dns, dsq=dsq,
            duration=_format_seconds(duration_value),
            gap_to_leader=_format_seconds(gap_to_leader_value),
        )
        if id_result is not None:
            logger.info('[RESULT] Resultado mapeado | driver_number=%s | id=%s', driver_number, id_result)


def session_result_api(session_key, id_session, drivers_map):
    dados = _api_get(OPENF1_BASE_URL + 'session_result', params={'session_key': session_key})
    if dados is None:
        logger.error('[RESULT] Nenhum dado recebido | session_key=%s', session_key)
        return
    logger.info('[RESULT] Registros recebidos: %s | session_key=%s', len(dados), session_key)
    _data_manipulation(dados, id_session, drivers_map)