from bs4 import BeautifulSoup
from src.app.modulos import utils 
from datetime import datetime
from dateutil import parser


patron_scoring = r'Corner, (.*?)\.'
patron_time =  r"(.*)(?=Corner,)"
patron_conceded = r'Conceded by (.*?)\.'

def scraping(url: str):
    driver = utils.driver_connection()

    driver.get(url)

    # Obtener el contenido HTML después de que JavaScript ha cargado
    html_content = driver.page_source

    # Cerrar el navegador
    driver.quit()

    # Analizar el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')


    date_extract = soup.find( class_='sdc-site-match-header__detail-time')
    date_extract = date_extract.get_text(strip=True)
    date_parsed = parser.parse(date_extract)
    date_play = date_parsed.strftime("%Y-%m-%d")
        
    elements = soup.find_all(class_='sdc-article-livetext__post')

    # Procesar y extraer la información de los elementos encontrados
    data = []
    home = ''
    away = ''
    
    
    for element in elements:
        text = element.get_text(strip=True)
        if 'Match ends,' in text:
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
            scoring_team, time, conceding_player = utils.matching_others(texto, patron_scoring, patron_time, patron_conceded)
            #time = utils.convert_time_str_to_int(time)
            corner = utils.standard_body(date_play, home, away, iteracion, texto, half, scoring_team, time, conceding_player)
            final_data.append(corner)
            iteracion = iteracion + 1
        
    return final_data
