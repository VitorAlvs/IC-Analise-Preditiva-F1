# db_insert.py
import logging
import os
import pyodbc
from dotenv import load_dotenv
import time

load_dotenv()

logger = logging.getLogger(__name__)

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=" + os.getenv('DB_SERVER', '') + ";"
    "DATABASE=" + os.getenv('DB_NAME', '') + ";"
    "UID=" + os.getenv('DB_USER', '') + ";"
    "PWD=" + os.getenv('DB_PASSWORD', '') + ";"
    "Connection Timeout=30;"
)

_connection = None

def _get_conn():
    global _connection
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            if _connection is None or _connection.closed:
                _connection = pyodbc.connect(conn_str, timeout=30)
            return _connection
        except pyodbc.Error as e:
            error_code = e.args[0] if e.args else ''
            # 40613 = banco indisponível (cold start Azure), 40501 = throttling
            if any(code in str(e) for code in ['40613', '40501', '40197', '10928']):
                wait = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
                logger.warning(
                    '[DB] Banco indisponivel (tentativa %s/%s). Aguardando %ss... | Erro: %s',
                    attempt + 1, max_attempts, wait, error_code
                )
                time.sleep(wait)
                _connection = None
                continue
            raise  # erro não-transitório, propaga imediatamente
    raise RuntimeError('[DB] Nao foi possivel conectar ao banco apos {} tentativas.'.format(max_attempts))


def buscar_inserir_Country(country_name):
    try:
        if not country_name:
            country_name = 'Unknown'
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT ID_Country FROM TB_Country WHERE country_name = ?', (country_name,))
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][COUNTRY] Inserindo: %s', country_name)
            cursor.execute('INSERT INTO TB_Country (country_name) VALUES (?)', (country_name,))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_Location(id_country, location_name):
    try:
        if not location_name:
            location_name = 'Unknown'
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID_Location FROM TB_Location WHERE location_name = ? AND ID_Country = ?',
            (location_name, id_country)
        )
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][LOCATION] Inserindo: %s', location_name)
            cursor.execute(
                'INSERT INTO TB_Location (ID_Country, location_name) VALUES (?,?)',
                (id_country, location_name)
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_Circuit(id_location, circuit_short_name, circuit_type):
    try:
        if not circuit_short_name:
            circuit_short_name = 'Unknown'
        if not circuit_type:
            circuit_type = 'Unknown'
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID_Circuit FROM TB_Circuit WHERE Circuit_short_name = ? AND ID_Location = ?',
            (circuit_short_name, id_location)
        )
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][CIRCUIT] Inserindo: %s', circuit_short_name)
            cursor.execute(
                'INSERT INTO TB_Circuit (ID_Location, Circuit_short_name, Circuit_type) VALUES (?,?,?)',
                (id_location, circuit_short_name, circuit_type)
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def inserir_Meeting(p):
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        id_country  = buscar_inserir_Country(p['country_name'])
        id_location = buscar_inserir_Location(id_country, p['location'])
        id_circuit  = buscar_inserir_Circuit(id_location, p['circuit_short_name'], p['circuit_type'])
        cursor.execute('SELECT ID_Meeting FROM TB_Meeting WHERE Meeting_API_Key = ?', (p['api_key'],))
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][MEETING] Inserindo: %s (%s)', p['meeting_name'], p['year'])
            cursor.execute(
                '''INSERT INTO TB_Meeting
                   (ID_Circuit, meeting_name, meeting_oficial_name, date_start, date_end,
                    gmt_offset, year, Meeting_API_Key)
                   VALUES (?,?,?,?,?,?,?,?)''',
                (id_circuit, p['meeting_name'], p['meeting_official_name'],
                 p['date_start'], p['date_end'], p['gmt_offset'], p['year'], p['api_key'])
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            logger.info('[DB][MEETING] Inserido | id=%s', new_id)
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_MeetingID(meeting_api_key):
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT ID_Meeting FROM TB_Meeting WHERE Meeting_API_Key = ?', (meeting_api_key,))
        row = cursor.fetchone()
        return row[0] if row else None
    except pyodbc.Error:
        raise


def buscar_inserir_SessionType(session_type):
    try:
        if not session_type:
            session_type = 'Unknown'
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT ID_SessionType FROM TB_SessionType WHERE session_type = ?', (session_type,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute('INSERT INTO TB_SessionType (session_type) VALUES (?)', (session_type,))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_SessionName(session_name):
    try:
        if not session_name:
            session_name = 'Unknown'
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT ID_SessionName FROM TB_SessionName WHERE session_name = ?', (session_name,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute('INSERT INTO TB_SessionName (session_name) VALUES (?)', (session_name,))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def inserir_Session(p):
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        id_meeting = buscar_MeetingID(p['meeting_key'])
        if id_meeting is None:
            logger.warning('[DB][SESSION] Meeting nao encontrada para api_key=%s', p['meeting_key'])
            return None
        id_session_type = buscar_inserir_SessionType(p['session_type'])
        id_session_name = buscar_inserir_SessionName(p['session_name'])
        cursor.execute('SELECT ID_Session FROM TB_Session WHERE Session_API_Key = ?', (p['api_key'],))
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][SESSION] Inserindo: %s | %s', p['session_name'], p['year'])
            cursor.execute(
                '''INSERT INTO TB_Session
                   (ID_Meeting, ID_SessionType, ID_SessionName, date_start, date_end,
                    gmt_offset, year, Session_API_Key)
                   VALUES (?,?,?,?,?,?,?,?)''',
                (id_meeting, id_session_type, id_session_name,
                 p['date_start'], p['date_end'], p['gmt_offset'], p['year'], p['api_key'])
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            logger.info('[DB][SESSION] Inserido | id=%s', new_id)
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_SessionID(session_api_key):
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT ID_Session FROM TB_Session WHERE Session_API_Key = ?', (session_api_key,))
        row = cursor.fetchone()
        return row[0] if row else None
    except pyodbc.Error:
        raise


def inserir_Weather(p):
    try:
        if p['id_session'] is None:
            logger.warning('[DB][WEATHER] id_session nulo, ignorado.')
            return
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM TB_Weather WHERE ID_Session = ? AND date = ?',
            (p['id_session'], p['date'])
        )
        if cursor.fetchone() is not None:
            return
        cursor.execute(
            '''INSERT INTO TB_Weather
               (ID_Session, date, air_temperature, track_temperature, humidity,
                pressure, wind_direction, wind_speed, rainfall)
               VALUES (?,?,?,?,?,?,?,?,?)''',
            (p['id_session'], p['date'], p['air_temperature'], p['track_temperature'],
             p['humidity'], p['pressure'], p['wind_direction'], p['wind_speed'], p['rainfall'])
        )
        conn.commit()
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_Driver(driver_number, first_name, last_name, full_name, name_acronym):
    try:
        full_parts = (full_name or '').split()
        if not first_name and len(full_parts) > 1:
            first_name = full_parts[0]
        if not last_name and len(full_parts) > 1:
            last_name = full_parts[-1]
        elif not last_name and len(full_parts) == 1:
            last_name = full_parts[0]
        if not full_name and first_name and last_name:
            full_name = first_name + ' ' + last_name
        if not full_name:
            full_name = 'Driver ' + str(driver_number)
        if not first_name:
            first_name = 'Driver' + str(driver_number)
        if not last_name:
            last_name = 'Unknown'
        if not name_acronym:
            cleaned = full_name.replace(' ', '')
            name_acronym = cleaned[:3].upper().ljust(3, 'X')
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID_Driver FROM TB_Driver WHERE driver_number = ? AND full_name = ?',
            (driver_number, full_name)
        )
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][DRIVER] Inserindo: %s | numero=%s', full_name, driver_number)
            cursor.execute(
                'INSERT INTO TB_Driver (driver_number, first_name, last_name, full_name, name_acronym) VALUES (?,?,?,?,?)',
                (driver_number, first_name, last_name, full_name, name_acronym)
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            logger.info('[DB][DRIVER] Inserido | id=%s', new_id)
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_Team(team_name, team_colour):
    try:
        if not team_name:
            team_name = 'Unknown Team'
        if not team_colour:
            team_colour = '000000'
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT ID_Team FROM TB_Team WHERE team_name = ?', (team_name,))
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][TEAM] Inserindo: %s', team_name)
            cursor.execute('INSERT INTO TB_Team (team_name, team_colour) VALUES (?,?)', (team_name, team_colour))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_DriverTeamYear(id_driver, id_team, season_year):
    try:
        if id_driver is None or id_team is None or season_year is None:
            return None
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID_DriverTeamYear FROM TB_DriverTeamYear WHERE ID_Driver = ? AND ID_Team = ? AND season_year = ?',
            (id_driver, id_team, season_year)
        )
        row = cursor.fetchone()
        if row is None:
            logger.info('[DB][DTY] Inserindo vinculo driver=%s, team=%s, year=%s', id_driver, id_team, season_year)
            cursor.execute(
                'INSERT INTO TB_DriverTeamYear (ID_Driver, ID_Team, season_year) VALUES (?,?,?)',
                (id_driver, id_team, season_year)
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise


def buscar_inserir_SessionResult(id_session, id_driver_team_year,
                                  position, number_of_laps,
                                  dnf, dns, dsq, duration, gap_to_leader):
    try:
        if any(v is None for v in [id_session, id_driver_team_year, position,
                                    number_of_laps, dnf, dns, dsq, duration, gap_to_leader]):
            return None
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID_SessionResult FROM TB_SessionResult WHERE ID_Session = ? AND ID_DriverTeamYear = ?',
            (id_session, id_driver_team_year)
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                '''INSERT INTO TB_SessionResult
                   (ID_Session, ID_DriverTeamYear, position, number_of_laps,
                    dnf, dns, dsq, duration, gap_to_leader)
                   VALUES (?,?,?,?,?,?,?,?,?)''',
                (id_session, id_driver_team_year, position, number_of_laps,
                 dnf, dns, dsq, duration, gap_to_leader)
            )
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        else:
            cursor.execute(
                '''UPDATE TB_SessionResult
                   SET position=?, number_of_laps=?, dnf=?, dns=?, dsq=?,
                       duration=?, gap_to_leader=?
                   WHERE ID_SessionResult=?''',
                (position, number_of_laps, dnf, dns, dsq, duration, gap_to_leader, row[0])
            )
            conn.commit()
            return row[0]
    except pyodbc.Error:
        _get_conn().rollback()
        raise