import API_meetingsOpenF1
import pyodbc
from pyodbc import connect

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=sql-f1-ic-br.database.windows.net;"
    "DATABASE=db_f1_analytics ;"  
    "UID=sysadmin;"          
    "PWD=!o)h7+<qw`*14G;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

connection = connect(conn_str)
cursor = connection.cursor()

#buscar e/ou inserir Country
def buscar_inserir_Country(country_name):

    try:

        country_name = country_name if country_name else 'Unknown Country'

        select_country_id = 'SELECT ID_Country FROM TB_Country WHERE country_name = ?'
        cursor.execute(select_country_id, (country_name,))
        country_row = cursor.fetchone()
        if country_row is not None:
            print(f'      [DB][COUNTRY] Encontrado por nome={country_name} | id={country_row[0]}')
            return country_row[0]

        print(f'      [DB][COUNTRY] Nao encontrado. Inserindo country={country_name}')

        insert_country  = 'INSERT INTO TB_Country (country_name) VALUES (?)'
        cursor.execute(insert_country, (country_name,))
        cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
        inserted_id = cursor.fetchone()[0]
        connection.commit()
        print(f'      [DB][COUNTRY] Inserido com id={inserted_id}')
        return inserted_id

    except pyodbc.Error as error:
        connection.rollback()
        raise

#buscar e/ou inserir Location
def buscar_inserir_Location(location_name, id_country = 0):

    try:

        if not location_name or id_country is None:
            return None

        select_location_id = 'SELECT ID_Location FROM TB_Location WHERE location_name = ?'
        cursor.execute(select_location_id, (location_name,))
        location_row = cursor.fetchone()

        if location_row is None:
            insert_location  = 'INSERT INTO TB_Location (ID_Country, location_name) VALUES (?,?)'
            cursor.execute(insert_location, (id_country, location_name))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            return inserted_id
        else:
            return location_row[0]
        
    except pyodbc.Error as error:
        connection.rollback()
        raise

#buscar e/ou inserir Circuit
def buscar_inserir_Circuit(id_location, circuit_name, circuit_type):

    try:

        if id_location is None or not circuit_name or not circuit_type:
            return None

        select_circuit_id = 'SELECT ID_Circuit FROM TB_Circuit WHERE Circuit_short_name = ?'
        cursor.execute(select_circuit_id, (circuit_name,))
        circuit_row = cursor.fetchone()

        if circuit_row is None:
            insert_circuit  = 'INSERT INTO TB_Circuit (ID_Location, Circuit_short_name, Circuit_type) VALUES (?,?,?)'
            cursor.execute(insert_circuit, (id_location, circuit_name, circuit_type))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            return inserted_id
        else:
            return circuit_row[0]
        
    except pyodbc.Error as error:
        connection.rollback()
        raise

def buscar_circuit_por_locationId(location_id):
    select_circuit_id = 'SELECT ID_Circuit FROM TB_Circuit WHERE ID_Location = ?'
    cursor.execute(select_circuit_id, (location_id,))
    circuit_row = cursor.fetchone()

    return circuit_row[0] if circuit_row is not None else None


#inserir Meetings
def inserir_Meeting(properties):

    circuit_name            = properties['circuit name']
    circuit_type            = properties['circuit type']
    location                = properties['location']
    country_name            = properties['country name']
    meeting_name            = properties['meeting_name']
    meeting_oficial_name    = properties['meeting_oficial_name']
    date_start              = properties['date_start']
    date_end                = properties['date_end']
    gmt_offset              = properties['gmt_offset']
    year                    = properties['year']
    api_key                 = properties['API key']

    if (not circuit_name or not circuit_type or not location or not country_name or
        not meeting_name or not meeting_oficial_name or not date_start or not date_end or not gmt_offset or
        year is None or api_key is None):
        return None

    #verificar Country
    country_id  = buscar_inserir_Country(country_name)
    if country_id is None:
        return None

    #verificar Location
    location_id = buscar_inserir_Location(location, country_id)
    if location_id is None:
        return None

    #verificar Circuit
    circuit_id  = buscar_inserir_Circuit(location_id, circuit_name, circuit_type)
    if circuit_id is None:
        return None

    try:

        select_meeting_id = 'SELECT ID_Meeting FROM TB_Meeting WHERE meeting_name = ? AND year = ?'
        cursor.execute(select_meeting_id, (meeting_name, year))
        meeting_id = cursor.fetchone()

        if meeting_id is None:
            insert_meeting  = 'INSERT INTO TB_meeting (ID_Circuit, meeting_name, meeting_oficial_name, date_start, date_end, gmt_offset, year, Meeting_API_Key) VALUES (?,?,?,?,?,?,?,?)'
            cursor.execute(insert_meeting, (circuit_id, meeting_name,meeting_oficial_name, date_start,date_end, gmt_offset, year, api_key))
            connection.commit()
            return
        else:
            return
        
    except pyodbc.Error as error:
        connection.rollback()
        raise

#Buscar ID_Meeting
def buscar_meeting(id_circuit, year):
    select_meeting_id = 'SELECT ID_Meeting FROM TB_Meeting WHERE ID_Circuit = ? AND year = ?'
    cursor.execute(select_meeting_id, (id_circuit, year))
    meeting_row = cursor.fetchone()

    return meeting_row[0] if meeting_row is not None else None


def buscar_meeting_por_api_key(meeting_api_key):
    select_meeting_id = 'SELECT ID_Meeting FROM TB_Meeting WHERE Meeting_API_Key = ?'
    cursor.execute(select_meeting_id, (meeting_api_key,))
    meeting_row = cursor.fetchone()

    return meeting_row[0] if meeting_row is not None else None

def buscar_inserir_SessionName(session_name):
    if not session_name:
        return None

    select_session_name = 'SELECT ID_SessionName FROM TB_SessionName WHERE session_name = ?'
    cursor.execute(select_session_name, (session_name,))
    session_row = cursor.fetchone()

    if session_row is None:
        insert_meeting  = 'INSERT INTO TB_SessionName (session_name) VALUES (?)'
        cursor.execute(insert_meeting, (session_name,))
        cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
        inserted_id = cursor.fetchone()[0]
        connection.commit()
        return inserted_id
    else:
        return session_row[0]

def buscar_inserir_SessionType(session_type):
    if not session_type:
        return None

    select_session_type = 'SELECT ID_SessionType FROM TB_SessionType WHERE session_type = ?'
    cursor.execute(select_session_type, (session_type,))
    session_row = cursor.fetchone()

    if session_row is None:
        insert_meeting  = 'INSERT INTO TB_SessionType (session_type) VALUES (?)'
        cursor.execute(insert_meeting, (session_type,))
        cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
        inserted_id = cursor.fetchone()[0]
        connection.commit()
        return inserted_id
    else:
        return session_row[0]

#Inserir Sessions
def inserir_Session(properties):
    session_type = properties['session type']
    session_name = properties['session name']
    location     = properties['location']
    date_start   = properties['date start']
    date_end     = properties['date end']
    gmt_offset   = properties['gmt_offset']
    year         = properties['year']
    api_key      = properties['API key']
    meeting_key  = properties.get('meeting key')

    if (not session_type or not session_name or not location or not date_start or not date_end or
        not gmt_offset or year is None or api_key is None):
        return None

    meeting_id = None

    # O payload de sessions fornece meeting_key; esse eh o vinculo mais confiavel.
    if meeting_key is not None:
        meeting_id = buscar_meeting_por_api_key(meeting_key)

    if meeting_id is None:
        country_name = properties.get('country name')
        country_id = buscar_inserir_Country(country_name)

        if country_id is None:
            return None

        if country_name:
            print(f'    [SESSION][MEETING] Buscando meeting por country_name={country_name} | year={year}')

        API_meetingsOpenF1.buscar_meeting_por_ano_pais(year, country_name)
        location_id = buscar_inserir_Location(location, country_id)
        circuit_id  = buscar_circuit_por_locationId(location_id)
        meeting_id  = buscar_meeting(circuit_id, year)

        if meeting_id is None:
            return None

    sessionName_id = buscar_inserir_SessionName(session_name)
    sessionType_id = buscar_inserir_SessionType(session_type)

    if sessionName_id is None or sessionType_id is None:
        return None

    try:
        if api_key is not None:
            select_session_id = 'SELECT ID_Session FROM TB_Session WHERE Session_API_Key = ?'
            cursor.execute(select_session_id, (api_key,))
        else:
            select_session_id = 'SELECT ID_Session FROM TB_Session WHERE ID_Meeting = ? AND ID_SessionName = ? AND date_start = ? AND year = ?'
            cursor.execute(select_session_id, (meeting_id, sessionName_id, date_start, year))

        session_row = cursor.fetchone()

        if session_row is None:
            insert_session = 'INSERT INTO TB_Session (ID_Meeting, ID_SessionType, ID_SessionName, date_start, date_end, gmt_offset, year, Session_API_Key) VALUES (?,?,?,?,?,?,?,?)'
            cursor.execute(insert_session, (
                meeting_id, sessionType_id, sessionName_id,
                date_start, date_end, gmt_offset, year, api_key
            ))
            connection.commit()
            return buscar_SessionID(api_key)
        else:
            return session_row[0]

    except pyodbc.Error:
        connection.rollback()
        raise

#Buscar Session por api_key
def buscar_SessionID(api_key):

    try:

        select_sessionID = 'SELECT ID_Session FROM TB_Session WHERE Session_API_Key = ?'
        cursor.execute(select_sessionID, (api_key,))
        session_row = cursor.fetchone()
        
        return session_row[0] if session_row is not None else None
        
    except pyodbc.Error as error:
        connection.rollback()
        raise


#Inserir weather
def inserir_Weather(properties):
    id_session          = properties['id_session'] 
    date                = properties['date']
    humidity            = properties['humidity']
    wind_speed          = properties['wind_speed']
    air_temperature     = properties['air_temperature']
    rainfall            = properties['rainfall']
    track_temperature   = properties['track_temperature']
    pressure            = properties['pressure']
    wind_direction      = properties['wind_direction']

    if (id_session is None or not date or humidity is None or wind_speed is None or air_temperature is None or
        rainfall is None or track_temperature is None or pressure is None or wind_direction is None):
        return None
    
    try:

        select_meeting_id = 'SELECT ID_Weather FROM TB_Weather WHERE ID_Session = ?'
        cursor.execute(select_meeting_id, (id_session))
        meeting_id = cursor.fetchone()

        if meeting_id is None:
            insert_weather  = 'INSERT INTO TB_Weather (ID_Session, date, air_temperature, track_temperature, humidity, pressure, wind_direction, wind_speed, rainfall) VALUES (?,?,?,?,?,?,?,?,?)'
            cursor.execute(insert_weather, (id_session, date, air_temperature, track_temperature, humidity, pressure, wind_direction, wind_speed, rainfall))
            connection.commit()
            return
        else:
            return
        
    except pyodbc.Error as error:
        connection.rollback()
        raise

#Buscar e/ou inserir Driver
def buscar_inserir_Driver(id_country, driver_number, first_name, last_name, full_name, name_acronym):
    try:
        if driver_number is None:
            return None

        if id_country is None:
            id_country = buscar_inserir_Country('Unknown Country')

        if not first_name and full_name:
            first_name = full_name.split(' ')[0]
        if not last_name and full_name:
            full_parts = full_name.split(' ')
            last_name = full_parts[-1] if len(full_parts) > 1 else full_parts[0]
        if not full_name and first_name and last_name:
            full_name = f'{first_name} {last_name}'
        if not full_name:
            full_name = f'Driver {driver_number}'
        if not first_name:
            first_name = f'Driver{driver_number}'
        if not last_name:
            last_name = 'Unknown'
        if not name_acronym:
            cleaned_name = full_name.replace(' ', '')
            name_acronym = cleaned_name[:3].upper().ljust(3, 'X')

        select_driver = 'SELECT ID_Driver FROM TB_Driver WHERE driver_number = ? AND full_name = ?'
        cursor.execute(select_driver, (driver_number, full_name))
        row = cursor.fetchone()

        if row is None:
            print(f'      [DB][DRIVER] Nao encontrado. Inserindo driver={full_name} | numero={driver_number}')
            insert_driver = 'INSERT INTO TB_Driver (ID_Country, driver_number, first_name, last_name, full_name, name_acronym) VALUES (?,?,?,?,?,?)'
            cursor.execute(insert_driver, (
                id_country, driver_number, first_name, last_name, full_name, name_acronym
            ))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            print(f'      [DB][DRIVER] Inserido com id={inserted_id}')
            return inserted_id
        else:
            print(f'      [DB][DRIVER] Encontrado driver={full_name} | id={row[0]}')
            return row[0]

    except pyodbc.Error:
        connection.rollback()
        raise

#Buscar e/ou inserir Team
def buscar_inserir_Team(team_name, team_colour):
    try:
        if not team_name:
            team_name = 'Unknown Team'
        if not team_colour:
            team_colour = '000000'

        select_team = 'SELECT ID_Team FROM TB_Team WHERE team_name = ?'
        cursor.execute(select_team, (team_name,))
        row = cursor.fetchone()

        if row is None:
            print(f'      [DB][TEAM] Nao encontrado. Inserindo team={team_name}')
            insert_team = 'INSERT INTO TB_Team (team_name, team_colour) VALUES (?,?)'
            cursor.execute(insert_team, (team_name, team_colour))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            print(f'      [DB][TEAM] Inserido com id={inserted_id}')
            return inserted_id
        else:
            print(f'      [DB][TEAM] Encontrado team={team_name} | id={row[0]}')
            return row[0]

    except pyodbc.Error:
        connection.rollback()
        raise

#Criar a relação Driver-Team-Year
def buscar_inserir_DriverTeamYear(id_driver, id_team, season_year):
    try:
        if id_driver is None or id_team is None or season_year is None:
            return None

        select_dty = 'SELECT ID_DriverTeamYear FROM TB_DriverTeamYear WHERE ID_Driver = ? AND ID_Team = ? AND season_year = ?'
        cursor.execute(select_dty, (id_driver, id_team, season_year))
        row = cursor.fetchone()

        if row is None:
            print(f'      [DB][DTY] Nao encontrado. Inserindo vinculo driver={id_driver}, team={id_team}, year={season_year}')
            insert_dty = 'INSERT INTO TB_DriverTeamYear (ID_Driver, ID_Team, season_year) VALUES (?,?,?)'
            cursor.execute(insert_dty, (id_driver, id_team, season_year))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            print(f'      [DB][DTY] Inserido com id={inserted_id}')
            return inserted_id
        else:
            print(f'      [DB][DTY] Encontrado vinculo driver={id_driver}, team={id_team}, year={season_year} | id={row[0]}')
            return row[0]

    except pyodbc.Error:
        connection.rollback()
        raise

#Buscar e/ou inserir Serrion result
def buscar_inserir_SessionResult(id_session, id_driver_team_year,
                                 position, number_of_laps,
                                 dnf, dns, dsq,
                                 duration, gap_to_leader):
    try:
        if (id_session is None or id_driver_team_year is None or position is None or number_of_laps is None or
            dnf is None or dns is None or dsq is None or duration is None or gap_to_leader is None):
            return None

        select_sr = 'SELECT ID_SessionResult FROM TB_SessionResult WHERE ID_Session = ? AND ID_DriverTeamYear = ?'
        cursor.execute(select_sr, (id_session, id_driver_team_year))
        row = cursor.fetchone()

        if row is None:
            insert_sr = 'INSERT INTO TB_SessionResult (ID_Session, ID_DriverTeamYear, position, number_of_laps, dnf, dns, dsq, duration, gap_to_leader) VALUES (?,?,?,?,?,?,?,?,?)'
            cursor.execute(insert_sr, (
                id_session, id_driver_team_year,
                position, number_of_laps,
                dnf, dns, dsq,
                duration, gap_to_leader
            ))
            cursor.execute('SELECT CAST(SCOPE_IDENTITY() AS INT)')
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            return inserted_id
        else:
            return row[0]

    except pyodbc.Error:
        connection.rollback()
        raise