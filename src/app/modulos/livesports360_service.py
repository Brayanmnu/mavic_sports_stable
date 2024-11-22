from bs4 import BeautifulSoup
from src.app.modulos import utils 
from datetime import datetime

patron_scoring = r'Corner, (.*?)\.'
patron_time =  r"(.*)(?=: Corner,)"
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
    
    date_extract = soup.find( id='gameDate4')
    date_extract = date_extract.get_text(strip=True)
    date_obj = datetime.strptime(date_extract, '%b %d, %Y, %I:%M %p')
    date_play = date_obj.strftime('%Y-%m-%d')
    
    # Encontrar todos los elementos con la clase 'Opta-Striped'
    ul_element = soup.find('ul', class_='ps-3')

    # Procesar y extraer la información de los elementos encontrados
    data = []
    home = ''
    away = ''
    if ul_element:
        li_elements = ul_element.find_all('li')
        iteracion = 1
        half = ''
        for element in li_elements:
            text = element.get_text(strip=True)
            if 'Match ends,' in text:
                home, away = utils.get_home_away_team(text)
             
        for element in li_elements:
            text = element.get_text(strip=True)
            
            if 'First Half begins' in text:
                half = '1H'
            elif 'Second Half begins' in text:
                half = '2H'
            if 'Corner' in text:
                scoring_team, time, conceding_player = utils.matching_others(text, patron_scoring, patron_time, patron_conceded)
                corner = utils.standard_body(date_play, home, away, iteracion, text, half, scoring_team, time, conceding_player)
                data.append(corner)
                iteracion = iteracion + 1

    
    return data