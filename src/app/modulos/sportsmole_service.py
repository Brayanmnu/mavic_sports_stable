import requests
from bs4 import BeautifulSoup
from src.app.modulos import utils 
from datetime import datetime
from dateutil import parser
import re

pattern_format_date = r'\s+\d{1,2}\.\d{2}(am|pm)'
patron_scoring = r'Corner - (.*?)\.'
patron_time =  r"(.*)(?=Corner - )"
patron_conceded = r'Conceded by (.*?)\.'


def scraping(url: str):
    # URL de la página web
    table_data = []
    # Realizar la solicitud HTTP a la página web
    response = requests.get(url)

    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        # Crear un objeto BeautifulSoup para analizar el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        date_extract = soup.find (attrs={"itemprop": "startDate"})
        date_extract = date_extract.get_text(strip=True)
        date_str_cleaned = date_extract.replace(" at", "").replace(" UK", "")
        date_str_cleaned = re.sub(pattern_format_date, '', date_str_cleaned)
        
        date_parsed = parser.parse(date_str_cleaned)
        date_play = date_parsed.strftime("%Y-%m-%d")
        print('obtuvo la fecha')
        # Encontrar la tabla con la clase 'tBc rem1a'
        tabla = soup.find('table', class_='tBc rem1a')

        home = ''
        away = ''
        
        if tabla:
            # Extraer todas las filas de la tabla
            filas = tabla.find_all('tr')
            print('obtuvo el tr')
            # Iterar sobre las filas y extraer los datos de las celdas
            iteracion = 1
            
            for fila in filas:
                celdas = fila.find('td')
                text = celdas.get_text(strip=True)
                if 'Game finished' in text:
                    text =  text.replace('- 1.','-')
                    home, away = utils.get_home_away_team(text)
                    print('Obtuvo los equipos')
            
            for fila in filas:
                celdas = fila.find('td')
                text = celdas.get_text(strip=True)
                text =  text.replace('- 1.','-')
                if 'First Half starts' in text:
                    half = '1H'
                elif 'Second Half starts' in text:
                    half = '2H'
                if 'Corner - ' in text:
                    scoring_team, time, conceding_player = utils.matching_others(text, patron_scoring, patron_time, patron_conceded)
                    corner = utils.standard_body(date_play, home, away, iteracion, text, half, scoring_team, time, conceding_player)
                    table_data.append(corner)
                    iteracion = iteracion + 1
                #celdas = [celda.get_text(strip=True) for celda in celdas if 'Corner' in celda.get_text(strip=True)]
                
    return table_data