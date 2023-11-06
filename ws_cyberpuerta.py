import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Web driver para EDGE
# s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
# driver = webdriver.Edge(service=s)

# Web driver para Chrome
webdriver_path = 'C:/Users/Alejandro/chrome/chromedriver.exe'
driver = webdriver.Chrome(webdriver_path)


def close_popups(driver_):
    # Lista de selectores comunes de botones de cerrar pop-ups
    close_button_selectors = [
        'button.close',
        'div.popup-close',
        'a.popup-close',
    ]

    # Intenta encontrar y hacer clic en los botones de cerrar
    for selector in close_button_selectors:
        try:
            close_button = WebDriverWait(driver_, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            close_button.click()
        except Exception as e:
            print(f"No se encontró o no se pudo hacer clic en el pop-up con el selector: {selector}. Error: {e}")


def scrape_cyberpuerta(URL):
    # Abre la URL
    driver.get(URL)

    # Intenta cerrar cualquier pop-up que aparezca
    close_popups(driver)

    # Espera explícita para que la página cargue y se muestren los productos
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'li.cell.productData'))
    )

    # Obtén el contenido de la página
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Lista para almacenar la información de los monitores
    monitors = []

    # Encuentra los elementos que contienen la información de los monitores
    monitor_elements = soup.find_all('li', class_=re.compile(r'cell productData small-12 small-order-\d+'))

    for monitor_element in monitor_elements:
        title = monitor_element.select_one('a.emproduct_right_title').text.strip()
        price = monitor_element.find('label', {'class': 'price'}).text.strip()
        resolution = monitor_element.find(string=re.compile('Resolución de la pantalla')).findNext('span').text.strip()
        screen_size = monitor_element.find(string=re.compile('Diagonal de la pantalla')).findNext('span').text.strip()
        # Obtener la URL de la imagen de fondo del div con clase 'cs-image'
        image_style = monitor_element.select_one('div.cs-image')['style']
        image_url = re.search(r'url\("(.+?)"\)', image_style).group(1)

        # Añade la información del monitor a la lista
        monitors.append({
            'Titulo': title,
            'Precio': price,
            'Resolución': resolution,
            'Tamaño de pantalla': screen_size,
            'URL Imagen': image_url,
            'Tienda': 'Cyberpuerta'
        })

    return monitors


# Lista de URLs a scrapear
urls = [
    'https://www.cyberpuerta.mx/Audio-y-Video/TV-y-Pantallas/Pantallas/Filtro/Tipo-HD/HD/',
    'https://www.cyberpuerta.mx/Pantallas-FullHD/',
    'https://www.cyberpuerta.mx/TV-4K-Ultra-HD/'
]

# DataFrame para recopilar los datos de todas las URLs
all_monitors = pd.DataFrame()

for url in urls:
    # Scrapear cada URL y añadir los datos al DataFrame
    monitors_data = scrape_cyberpuerta(url)
    all_monitors = pd.concat([all_monitors, pd.DataFrame(monitors_data)], ignore_index=True)

# Mostrar los datos recolectados
print(all_monitors)

# Guardar los datos en un archivo CSV
all_monitors.to_excel('pantallas_cyberpuerta.xlsx', index=False)

# Cerrar el WebDriver
driver.quit()
