from bs4 import BeautifulSoup
from src.app.modulos import utils 
import re
import requests

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
    final_data = []
    headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
   
    response = requests.get(url, headers=headers)

    # Mostrar las cookies establecidas por el servidor
    print(response.cookies)
    for cookie in response.cookies:
        print(cookie.name, cookie.value)
        
        
    if response.status_code == 200:
        # Analizar el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
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
                    home, away = utils.get_home_away_team(text)
                data.append(text)
        
        iteracion = 1
        half = ''
        
        
        for texto in reversed(data):
            if 'First Half begins.' in texto:
                half = '1H'
            elif 'Second Half begins' in texto:
                half = '2H'
            if 'Corner' in texto:
                scoring_team, time, conceding_player = utils.matching_others(texto, patron_scoring, patron_time, patron_conceded)
                corner = utils.standard_body(date_play, home, away, iteracion, texto, half, scoring_team, time, conceding_player)
                final_data.append(corner)
                iteracion = iteracion + 1
        
    return final_data
