from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import re
import os
import psycopg2
from dotenv import load_dotenv



# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def driver_connection () :
    # Configurar opciones de Edge
    options = Options()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument("headless")
    options.use_chromium = True  # Asegúrate de que está configurado para usar Chromium

    # Especificar la ruta a EdgeDriver si no está en el PATH
    # edge_driver_path = 'D:\\PROYECTOS\\MAVIC\\mavic_app\\edgedriver_win64\\msedgedriver.exe'
    edge_driver_path = 'msedgedriver.exe'
    
    # Crear un servicio de EdgeDriver
    service = Service(edge_driver_path)

    # Inicializar el WebDriver para Edge
    driver = webdriver.Edge(service=service, options=options)
    
    return driver


def matching (texto:str, patron: str):
    print(f'Texto a procesar: {texto}')
    print(f'Patron a procesar: {patron}')
    texto_capturado=''
    resultado = re.search(patron, texto)
    # Verificar si se encontró el patrón
    if resultado:
        # Extraer y mostrar el texto capturado
        texto_capturado = resultado.group(1)
    else:
        print("No se encontró el patrón en el texto.")
    return texto_capturado


def standard_body(date_play:str, home:str, away:str, contador:int, narracion: str, half:str, scoring_team: str, time:str, conceding_player:str):
    
    response = {
        'date': date_play,
        'home_team': home.strip(),
        'away_team': away.strip(),
        'corner_count' : contador,
        'scoring_team': scoring_team.strip(),
        'half': half,
        'time':time,
        'conceding_player':conceding_player.strip()
    }
    
    return response



def matching_others(narracion: str, patron_scoring: str, patron_time: str, patron_conceded: str):
    print('Procesamiento de scoring_team ')
    scoring_team = matching(narracion, patron_scoring)
    print('Procesamiento de time ')
    time = matching(narracion, patron_time)
    time = convert_time_str_to_int(time)
    print('Procesamiento de conceding_player ')
    conceding_player = matching(narracion, patron_conceded)
    
    return scoring_team, time, conceding_player
    
    
def convert_time_str_to_int(time_str:str):
    time_str = time_str.replace("'","")
    time_array = []
    time_array = time_str.split('+')

    suma_time = 0
    for time in time_array:
        suma_time =  suma_time + int(time)
    
    return suma_time


def conexion_postgres(host:str , port: str, db: str, usr:str, pwd:str):
    conn = psycopg2.connect(host=host, port=port, database=db, user=usr,password=pwd)
    return conn


def get_values_database_postgress():
    host = os.getenv('databaseHost') 
    port = os.getenv('databasePort')
    db = os.getenv('databaseName')
    usr = os.getenv('databaseUsr')
    pwd = os.getenv('databasePwd')
    return host, port, db, usr, pwd

def get_home_away_team(text:str):
    print(f'texto: {text}')
    pattern_teams = r'\b([\w\sáéíóúñÁÉÍÓÚÑüÜöÖ()\-]+(?:\s\d+)?[\w\sáéíóúñÁÉÍÓÚÑüÜöÖ()\-]*)\s\d'
    matches_team = re.findall(pattern_teams, text)
    home, away = matches_team
    home= home.replace('Game finished -','')
    return home, away