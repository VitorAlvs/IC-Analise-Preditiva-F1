# app.py
import logging
import API_meetingsOpenF1
import API_sessionsOpenF1

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('=== Iniciando carga OpenF1 ===')
    logger.info('--- Carregando Meetings ---')
    API_meetingsOpenF1.meetings_all()
    logger.info('--- Carregando Sessions, Weather, Drivers e Results ---')
    API_sessionsOpenF1.sessions_api()
    logger.info('=== Carga finalizada ===')