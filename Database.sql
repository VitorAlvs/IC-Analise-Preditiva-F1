-- 1. Criação da tabela TB_Country
CREATE TABLE TB_Country (
    ID_Country INT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR(100),
    country_code CHAR(3)
);

-- 2. Criação da tabela TB_Location (depende de TB_Country)
CREATE TABLE TB_Location (
    ID_Location INT IDENTITY(1,1) PRIMARY KEY,
    ID_Country INT,
    location_name VARCHAR(100),
    CONSTRAINT FK_Location_Country FOREIGN KEY (ID_Country) REFERENCES TB_Country(ID_Country)
);

-- 3. Criação da tabela TB_Circuit (depende de TB_Location)
CREATE TABLE TB_Circuit (
    ID_Circuit INT IDENTITY(1,1) PRIMARY KEY,
    ID_Location INT,
    Circuit_short_name VARCHAR(100),
    Circuit_type VARCHAR(50),
    CONSTRAINT FK_Circuit_Location FOREIGN KEY (ID_Location) REFERENCES TB_Location(ID_Location)
);

-- 4. Criação da tabela TB_Meeting (depende de TB_Circuit)
CREATE TABLE TB_Meeting (
    ID_Meeting INT IDENTITY(1,1) PRIMARY KEY,
    ID_Circuit INT,
    meeting_name VARCHAR(100),
    meeting_oficial_name VARCHAR(255),
    date_start DATETIMEOFFSET,
    date_end DATETIMEOFFSET,
    gmt_offset VARCHAR(10),
    year INT,
    Meeting_API_Key INT,
    CONSTRAINT FK_Meeting_Circuit FOREIGN KEY (ID_Circuit) REFERENCES TB_Circuit(ID_Circuit)
);

-- 5. Criação da tabela TB_SessionType
CREATE TABLE TB_SessionType (
    ID_SessionType INT IDENTITY(1,1) PRIMARY KEY,
    session_type VARCHAR(20)
);

-- 6. Criação da tabela TB_SessionName
CREATE TABLE TB_SessionName (
    ID_SessionName INT IDENTITY(1,1) PRIMARY KEY,
    session_name VARCHAR(30)
);

--7. Criação da tabela TB_Session (depende de TB_Meeting, TB_SessionType, TB_SessionName)
CREATE TABLE TB_Session (
    ID_Session INT IDENTITY(1,1) PRIMARY KEY,
    ID_Meeting INT,
    ID_SessionType INT,
    ID_SessionName INT,
    date_start DATETIMEOFFSET,
    date_end DATETIMEOFFSET,    
    gmt_offset VARCHAR(10),
    year INT, 
    Session_API_Key INT,
    CONSTRAINT FK_Session_Meeting FOREIGN KEY (ID_Meeting) REFERENCES TB_Meeting(ID_Meeting),
    CONSTRAINT FK_Session_Type FOREIGN KEY (ID_SessionType) REFERENCES TB_SessionType(ID_SessionType),
    CONSTRAINT FK_Session_Name FOREIGN KEY (ID_SessionName) REFERENCES TB_SessionName(ID_SessionName)
);

--8. Criação da tabela TB_Weather (depende de TB_Session)
CREATE TABLE TB_Weather (
    ID_Weather INT IDENTITY(1,1) PRIMARY KEY,
    ID_Session INT, 
    date DATETIMEOFFSET,
    air_temperature DECIMAL(5,2),   
    track_temperature DECIMAL(5,2), 
    humidity TINYINT,               
    pressure DECIMAL(6,2),          
    wind_direction SMALLINT,        
    wind_speed DECIMAL(5,2),        
    rainfall TINYINT,               
    
    CONSTRAINT FK_Weather_Session FOREIGN KEY (ID_Session) REFERENCES TB_Session(ID_Session)
);