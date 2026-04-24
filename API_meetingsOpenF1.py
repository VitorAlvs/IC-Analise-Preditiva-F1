# API_meetingsOpenF1.py
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


def _meeting_to_properties(each):
    return {
        'circuit_short_name':    each.get('circuit_short_name', 'Unknown'),
        'circuit_type':          each.get('circuit_type', 'Unknown'),
        'location':              each.get('location', 'Unknown'),
        'country_name':          each.get('country_name', 'Unknown'),
        'meeting_name':          each.get('meeting_name', 'Unknown'),
        'meeting_official_name': each.get('meeting_official_name', ''),
        'date_start':            each.get('date_start'),
        'date_end':              each.get('date_end'),
        'gmt_offset':            each.get('gmt_offset', '+00:00'),
        'year':                  each.get('year'),
        'api_key':               each.get('meeting_key'),
    }


def _data_manipulation(meetings):
    processed = set()
    for each in meetings:
        meeting_key = each.get('meeting_key')
        if meeting_key in processed:
            continue
        processed.add(meeting_key)
        props = _meeting_to_properties(each)
        logger.info('[MEETING] Processando: %s (%s)', props['meeting_name'], props['year'])
        db_insert.inserir_Meeting(props)


def meetings_all(year=None):
    logger.info('[MEETING] Iniciando carga de meetings...')
    params = {}
    if year:
        params['year'] = year
    dados = _api_get(OPENF1_BASE_URL + 'meetings', params=params)
    if dados is None:
        logger.error('[MEETING] Nenhum dado recebido da API.')
        return
    logger.info('[MEETING] Total retornado: %s', len(dados))
    _data_manipulation(dados)