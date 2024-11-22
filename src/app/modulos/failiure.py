from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import time

# Configurar opciones de Edge
options = Options()
options.use_chromium = True  # Asegúrate de que está configurado para usar Chromium

# Especificar la ruta a EdgeDriver si no está en el PATH
edge_driver_path = 'D:\\PROYECTOS\\MAVIC\\edgedriver_win64\\msedgedriver.exe'

# Crear un servicio de EdgeDriver
service = Service(edge_driver_path)

# Inicializar el WebDriver para Edge
driver = webdriver.Edge(service=service, options=options)

# Navegar a la URL deseada
url = 'https://www.mlssoccer.com/competitions/mls-regular-season/2024/matches/lafcvsrsl-07-17-2024/feed'
driver.get(url)

def scroll_to_end(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Desplazarse hacia abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Esperar a que la página cargue
        time.sleep(8)
        # Calcular la nueva altura de la página y compararla con la altura anterior
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Hacer scroll hasta el final de la página
scroll_to_end(driver)


# Obtener el contenido HTML de la página
html_content = driver.page_source

# Cerrar el navegador
driver.quit()

# Analizar el contenido HTML con BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')


print(soup)

div_elements = soup.find_all('div', class_='mls-o-match-feed__container')


# Procesar y extraer la información de los elementos encontrados
data = []
for element in div_elements:
    text = element.get_text(strip=True)
    #if 'Corner' in text:
    data.append(text)

# Imprimir la información extraída
for item in data:
    print(item)
