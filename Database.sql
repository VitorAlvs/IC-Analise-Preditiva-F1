-- 1. Criação da tabela TB_Country (Tabela Independente)
CREATE TABLE TB_Country (
    ID_Country INT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL
);

-- 2. Criação da tabela TB_Location (Depende de TB_Country)
CREATE TABLE TB_Location (
    ID_Location INT IDENTITY(1,1) PRIMARY KEY,
    ID_Country INT NOT NULL,
    location_name VARCHAR(100) NOT NULL,
    CONSTRAINT FK_Location_Country FOREIGN KEY (ID_Country) REFERENCES TB_Country(ID_Country)
);

-- 3. Criação da tabela TB_Circuit (Depende de TB_Location)
CREATE TABLE TB_Circuit (
    ID_Circuit INT IDENTITY(1,1) PRIMARY KEY,
    ID_Location INT NOT NULL,
    Circuit_short_name VARCHAR(100) NOT NULL,
    Circuit_type VARCHAR(50) NOT NULL,
    CONSTRAINT FK_Circuit_Location FOREIGN KEY (ID_Location) REFERENCES TB_Location(ID_Location)
);

-- 4. Criação da tabela TB_Meeting (Depende de TB_Circuit)
CREATE TABLE TB_Meeting (
    ID_Meeting INT IDENTITY(1,1) PRIMARY KEY,
    ID_Circuit INT NOT NULL,
    meeting_name VARCHAR(100) NOT NULL,
    meeting_oficial_name VARCHAR(255) NOT NULL,
    date_start DATETIMEOFFSET NOT NULL,
    date_end DATETIMEOFFSET NOT NULL,
    gmt_offset VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    Meeting_API_Key INT NOT NULL,
    CONSTRAINT FK_Meeting_Circuit FOREIGN KEY (ID_Circuit) REFERENCES TB_Circuit(ID_Circuit)
);

-- 5. Criação da tabela TB_SessionType (Tabela Independente)
CREATE TABLE TB_SessionType (
    ID_SessionType INT IDENTITY(1,1) PRIMARY KEY,
    session_type VARCHAR(20) NOT NULL
);

-- 6. Criação da tabela TB_SessionName (Tabela Independente)
CREATE TABLE TB_SessionName (
    ID_SessionName INT IDENTITY(1,1) PRIMARY KEY,
    session_name VARCHAR(30) NOT NULL
);

-- 7. Criação da tabela TB_Session (Depende de TB_Meeting, TB_SessionType, TB_SessionName)
CREATE TABLE TB_Session (
    ID_Session INT IDENTITY(1,1) PRIMARY KEY,
    ID_Meeting INT NOT NULL,
    ID_SessionType INT NOT NULL,
    ID_SessionName INT NOT NULL,
    date_start DATETIMEOFFSET NOT NULL,
    date_end DATETIMEOFFSET NOT NULL,    
    gmt_offset VARCHAR(10) NOT NULL,
    year INT NOT NULL, 
    Session_API_Key INT NOT NULL,
    CONSTRAINT FK_Session_Meeting FOREIGN KEY (ID_Meeting) REFERENCES TB_Meeting(ID_Meeting),
    CONSTRAINT FK_Session_Type FOREIGN KEY (ID_SessionType) REFERENCES TB_SessionType(ID_SessionType),
    CONSTRAINT FK_Session_Name FOREIGN KEY (ID_SessionName) REFERENCES TB_SessionName(ID_SessionName)
);

-- 8. Criação da tabela TB_Weather (Depende de TB_Session)
CREATE TABLE TB_Weather (
    ID_Weather INT IDENTITY(1,1) PRIMARY KEY,
    ID_Session INT NOT NULL, 
    date DATETIMEOFFSET NOT NULL,
    air_temperature DECIMAL(5,2) NOT NULL,   
    track_temperature DECIMAL(5,2) NOT NULL, 
    humidity TINYINT NOT NULL,               
    pressure DECIMAL(6,2) NOT NULL,          
    wind_direction SMALLINT NOT NULL,        
    wind_speed DECIMAL(5,2) NOT NULL,        
    rainfall TINYINT NOT NULL,               
    CONSTRAINT FK_Weather_Session FOREIGN KEY (ID_Session) REFERENCES TB_Session(ID_Session)
);

-- 9. Criação da tabela TB_Driver (Depende de TB_Country)
CREATE TABLE TB_Driver (
    ID_Driver INT IDENTITY(1,1) PRIMARY KEY,
    ID_Country INT NOT NULL, 
    driver_number INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    name_acronym CHAR(3) NOT NULL,
    CONSTRAINT FK_Driver_Country FOREIGN KEY (ID_Country) REFERENCES TB_Country(ID_Country)
);

-- 10. Criação da tabela TB_Team (Tabela Independente)
CREATE TABLE TB_Team (
    ID_Team INT IDENTITY(1,1) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_colour CHAR(6) NOT NULL
);

-- 11. Criação da tabela associativa TB_DriverTeamYear (Depende de TB_Driver e TB_Team)
CREATE TABLE TB_DriverTeamYear (
    ID_DriverTeamYear INT IDENTITY(1,1) PRIMARY KEY,
    ID_Driver INT NOT NULL,
    ID_Team INT NOT NULL,
    season_year INT NOT NULL,
    CONSTRAINT FK_DriverTeamYear_Driver FOREIGN KEY (ID_Driver) REFERENCES TB_Driver(ID_Driver),
    CONSTRAINT FK_DriverTeamYear_Team FOREIGN KEY (ID_Team) REFERENCES TB_Team(ID_Team),
    -- Regra extra para evitar duplicar o mesmo piloto na mesma equipe no mesmo ano
    CONSTRAINT UQ_DriverSeat UNIQUE (ID_Driver, ID_Team, season_year)
);

-- 12. Criação da tabela TB_SessionResult (Depende de TB_Session e TB_DriverTeamYear)
CREATE TABLE TB_SessionResult (
    ID_SessionResult INT IDENTITY(1,1) PRIMARY KEY,
    ID_Session INT NOT NULL,
    ID_DriverTeamYear INT NOT NULL,
    position INT NOT NULL,
    number_of_laps INT NOT NULL,
    dnf BIT NOT NULL, 
    dns BIT NOT NULL,
    dsq BIT NOT NULL,
    duration VARCHAR(100) NOT NULL,
    gap_to_leader VARCHAR(100) NOT NULL,
    CONSTRAINT FK_SessionResult_Session FOREIGN KEY (ID_Session) REFERENCES TB_Session(ID_Session),
    CONSTRAINT FK_SessionResult_DriverTeam FOREIGN KEY (ID_DriverTeamYear) REFERENCES TB_DriverTeamYear(ID_DriverTeamYear)
);
