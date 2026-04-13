import API_meetingsOpenF1
import pyodbc
from pyodbc import connect

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=F1Data;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)
connection = connect(conn_str)
cursor = connection.cursor()

#buscar e/ou inserir Country
def buscar_inserir_Country(country_name, country_code):

    try:

        select_country_id = 'SELECT ID_Country FROM TB_Country WHERE country_name = ?'
        cursor.execute(select_country_id, (country_name,))
        country_row = cursor.fetchone()

        if country_row is None:
            insert_country  = 'INSERT INTO TB_Country (country_name, country_code) VALUES (?,?)'
            cursor.execute(insert_country, (country_name, country_code))
            connection.commit()
            return buscar_inserir_Country(country_name, country_code)
        else:
            return country_row[0]

    except pyodbc.Error as error:
        connection.rollback()
        raise

#buscar e/ou inserir Location
def buscar_inserir_Location(location_name, id_country = 0):

    try:

        select_location_id = 'SELECT ID_Location FROM TB_Location WHERE location_name = ?'
        cursor.execute(select_location_id, (location_name,))
        location_row = cursor.fetchone()

        if location_row is None:
            insert_location  = 'INSERT INTO TB_Location (ID_Country, location_name) VALUES (?,?)'
            cursor.execute(insert_location, (id_country, location_name))
            connection.commit()
            return buscar_inserir_Location(location_name, id_country)
        else:
            return location_row[0]
        
    except pyodbc.Error as error:
        connection.rollback()
        raise

#buscar e/ou inserir Circuit
def buscar_inserir_Circuit(id_location, circuit_name, circuit_type):

    try:

        select_circuit_id = 'SELECT ID_Circuit FROM TB_Circuit WHERE Circuit_short_name = ?'
        cursor.execute(select_circuit_id, (circuit_name,))
        circuit_row = cursor.fetchone()

        if circuit_row is None:
            insert_circuit  = 'INSERT INTO TB_Circuit (ID_Location, Circuit_short_name, Circuit_type) VALUES (?,?,?)'
            cursor.execute(insert_circuit, (id_location, circuit_name, circuit_type))
            connection.commit()
            return buscar_inserir_Circuit(id_location, circuit_name, circuit_type)
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
    country_code            = properties['country_code']
    meeting_name            = properties['meeting_name']
    meeting_oficial_name    = properties['meeting_oficial_name']
    date_start              = properties['date_start']
    date_end                = properties['date_end']
    gmt_offset              = properties['gmt_offset']
    year                    = properties['year']

    #verificar Country
    country_id  = buscar_inserir_Country(country_name, country_code)

    #verificar Location
    location_id = buscar_inserir_Location(location, country_id)

    #verificar Circuit
    circuit_id  = buscar_inserir_Circuit(location_id, circuit_name, circuit_type)

    try:

        select_meeting_id = 'SELECT ID_Meeting FROM TB_Meeting WHERE meeting_name = ? AND year = ?'
        cursor.execute(select_meeting_id, (meeting_name, year))
        meeting_id = cursor.fetchone()

        if meeting_id is None:
            insert_meeting  = 'INSERT INTO TB_meeting (ID_Circuit, meeting_name, meeting_oficial_name, date_start, date_end, gmt_offset, year) VALUES (?,?,?,?,?,?,?)'
            cursor.execute(insert_meeting, (circuit_id, meeting_name,meeting_oficial_name, date_start,date_end, gmt_offset, year))
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

def buscar_inserir_SessionName(session_name):
    select_session_name = 'SELECT ID_SessionName FROM TB_SessionName WHERE session_name = ?'
    cursor.execute(select_session_name, (session_name,))
    session_row = cursor.fetchone()

    if session_row is None:
        insert_meeting  = 'INSERT INTO TB_SessionName (session_name) VALUES (?)'
        cursor.execute(insert_meeting, (session_name,))
        connection.commit()
        return buscar_inserir_SessionName(session_name)
    else:
        return session_row[0]

def buscar_inserir_SessionType(session_type):
    select_session_type = 'SELECT ID_SessionType FROM TB_SessionType WHERE session_type = ?'
    cursor.execute(select_session_type, (session_type,))
    session_row = cursor.fetchone()

    if session_row is None:
        insert_meeting  = 'INSERT INTO TB_SessionType (session_type) VALUES (?)'
        cursor.execute(insert_meeting, (session_type,))
        connection.commit()
        return buscar_inserir_SessionType(session_type)
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

    #Verificar ID da Meeting
    location_id      = buscar_inserir_Location(location)
    circuit_id       = buscar_circuit_por_locationId(location_id)
    meeting_id       = buscar_meeting(circuit_id, year)

    if meeting_id is None:
        country_name = properties.get('country name')
        if not country_name:
            return

        API_meetingsOpenF1.buscar_meeting_por_ano_pais(year, country_name)
        location_id = buscar_inserir_Location(location)
        circuit_id = buscar_circuit_por_locationId(location_id)
        meeting_id = buscar_meeting(circuit_id, year)

        if meeting_id is None:
            return

    #Verificar session name ID
    sessionName_id   = buscar_inserir_SessionName(session_name)

    #Verificar session type ID
    sessionType_id   = buscar_inserir_SessionType(session_type)

    try:
        
        select_session_id = 'SELECT ID_Session FROM TB_Session WHERE ID_Meeting = ? AND year = ?'
        cursor.execute(select_session_id, (meeting_id, year))
        session_row = cursor.fetchone()

        if session_row is None:
            insert_session  = 'INSERT INTO TB_Session (ID_Meeting, ID_SessionType, ID_SessionName, date_start, date_end, gmt_offset, year, Session_API_Key) VALUES (?,?,?,?,?,?,?,?)'
            cursor.execute(insert_session, (meeting_id, sessionType_id, sessionName_id, date_start, date_end, gmt_offset, year, api_key))
            connection.commit()
            return
        else:
            return
        
    except pyodbc.Error as error:
        connection.rollback()
        raise

   