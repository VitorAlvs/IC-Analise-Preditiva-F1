# API_sessionsOpenF1.py
import logging
import time
import requests
import db_insert
import API_weatherOpenF1
import API_DriversOpenF1
import API_sessionresultOpenF1
from config import OPENF1_BASE_URL, REQUEST_TIMEOUT, REQUEST_MAX_RETRIES, REQUEST_BACKOFF_BASE
from datetime import datetime, timezone 

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

def _data_manipulation(sessions):
    processed_sessions = set()
    for each in sessions:
        session_api_key = each.get('session_key')
        if session_api_key in processed_sessions:
            continue
        processed_sessions.add(session_api_key)

        year         = each.get('year')
        session_name = each.get('session_name', 'Unknown')
        location     = each.get('location', 'Unknown')

        # ── Ignora sessões futuras ────────────────────────────────────────────
        date_start_raw = each.get('date_start')
        if date_start_raw:
            try:
                # A API retorna formato ISO 8601 com offset (ex: "2026-05-02T11:30:00+00:00")
                date_start = datetime.fromisoformat(date_start_raw)
                # Garante que now() tenha timezone para comparação
                now = datetime.now(timezone.utc).astimezone(date_start.tzinfo)
                if date_start > now:
                    logger.info(
                        '[SESSION] Sessao futura ignorada: %s | %s | %s (data_start=%s)',
                        session_name, location, year, date_start_raw
                    )
                    continue
            except ValueError:
                logger.warning('[SESSION] Nao foi possivel interpretar date_start=%s', date_start_raw)
        # ─────────────────────────────────────────────────────────────────────

        logger.info('[SESSION] Processando: %s | %s | %s', session_name, location, year)

        props = {
            'session_type':          each.get('session_type', 'Unknown'),
            'session_name':          session_name,
            'location':              location,
            'circuit_short_name':    each.get('circuit_short_name'),
            'circuit_type':          each.get('circuit_type'),
            'country_name':          each.get('country_name'),
            'meeting_name':          each.get('meeting_name'),
            'meeting_official_name': each.get('meeting_official_name'),
            'meeting_key':           each.get('meeting_key'),
            'date_start':            date_start_raw,
            'date_end':              each.get('date_end'),
            'gmt_offset':            each.get('gmt_offset', '+00:00'),
            'api_key':               session_api_key,
            'year':                  year,
        }

        id_session = db_insert.inserir_Session(props)
        if id_session is None:
            logger.warning('[SESSION] Ignorada: meeting nao encontrada | session_key=%s', session_api_key)
            continue

        logger.info('[WEATHER] Carregando clima | session_key=%s', session_api_key)
        API_weatherOpenF1.weather_api(session_api_key, id_session)

        logger.info('[DRIVERS] Carregando pilotos/equipes | session_key=%s', session_api_key)
        drivers_map = API_DriversOpenF1.drivers_api(session_api_key, year)

        logger.info('[RESULT] Carregando resultados | session_key=%s', session_api_key)
        API_sessionresultOpenF1.session_result_api(session_api_key, id_session, drivers_map)
        API_sessionresultOpenF1.session_result_api(session_api_key, id_session, drivers_map)


def sessions_api(year=None, meeting_key=None):
    logger.info('[SESSION] Iniciando carga de sessions...')
    params = {}
    if year:
        params['year'] = year
    if meeting_key:
        params['meeting_key'] = meeting_key
    dados = _api_get(OPENF1_BASE_URL + 'sessions', params=params)
    if dados is None:
        logger.error('[SESSION] Nenhum dado recebido da API.')
        return
    logger.info('[SESSION] Total retornado: %s', len(dados))
    _data_manipulation(dados)