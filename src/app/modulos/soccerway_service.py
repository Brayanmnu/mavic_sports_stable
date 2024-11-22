from bs4 import BeautifulSoup
from src.app.modulos import utils 
import re
import time

patron_fecha = r'\d{4}/\d{2}/\d{2}'

patron_scoring = r'Corner, (.*?)\.'
patron_time =  r"(.*)(?=Corner,)"
patron_conceded = r'Conceded by (.*?)\.'

def obtener_fecha_url(url:str):
    match = re.search(patron_fecha, url)
    date = ''
    if match:
        date = match.group()
        date = date.replace('/', '-')
    else:
        print("No se encontró ninguna fecha en la URL.")
    
    return date
    
def scraping(url: str):
    driver = utils.driver_connection()
    driver.get(url)
    time.sleep(5)
    # Obtener el contenido HTML después de que JavaScript ha cargado
    html_content = driver.page_source

    # Cerrar el navegador
    driver.quit()

    # Analizar el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_play = obtener_fecha_url(url)
    
    # Encontrar todos los elementos con la clase 'Opta-Striped'
    ul_element = soup.find('ul', class_='Opta-Striped')
    # Procesar y extraer la información de los elementos encontrados
    data = []
    home = ''
    away = ''
    if ul_element:
        li_elements = ul_element.find_all('li')
        for element in li_elements:
            text = element.get_text(strip=True)
            if 'Match ends,' in text:
                text =  text.replace('- 1.','-')
                home, away = utils.get_home_away_team(text)
            data.append(text)
    
    iteracion = 1
    half = ''
    final_data = []
    for texto in reversed(data):
        if 'First Half begins.' in texto:
            half = '1H'
        elif 'Second Half begins' in texto:
            half = '2H'
        if 'Corner' in texto:
            scoring_team, time_corner, conceding_player = utils.matching_others(texto, patron_scoring, patron_time, patron_conceded)
            corner = utils.standard_body(date_play, home, away, iteracion, texto, half, scoring_team, time_corner, conceding_player)
            final_data.append(corner)
            iteracion = iteracion + 1
        
    return final_data
