import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import multiprocessing


# Función para realizar el scraping de Cyberpuerta y almacenar los resultados en el diccionario compartido
def scrape_cyberpuerta(urls, shared_dict, shared_dict_total):
    # Listas para almacenar los productos de cada categoría de resolución
    resolution_1_data = []
    resolution_2_data = []
    resolution_3_data = []

    for URL in urls:
        driver = setup_driver()
        # Abre la URL
        driver.get(URL)

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
            resolution = monitor_element.find(string=re.compile('Resolución de la pantalla')).findNext(
                'span').text.strip()
            screen_size = monitor_element.find(string=re.compile('Diagonal de la pantalla')).findNext(
                'span').text.strip()
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

        # Agregar los productos a las listas de cada categoría de resolución
        resolution_1_data.extend([product for product in monitors if '1366 x 768' in product['Resolución']])
        resolution_2_data.extend([product for product in monitors if '1920 x 1080' in product['Resolución']])
        resolution_3_data.extend([product for product in monitors if '3840 x 2160' in product['Resolución']])

        # Cerrar el WebDriver
        driver.quit()
        # update shared_dict_total with monitors
        shared_dict_total['cyberpuerta'].extend(monitors)

    # Encontrar el producto más económico en cada categoría de resolución después de procesar todas las URLs
    resolution_1_min = min(resolution_1_data, key=lambda x: x['Precio'])
    resolution_2_min = min(resolution_2_data, key=lambda x: x['Precio'])
    resolution_3_min = min(resolution_3_data, key=lambda x: x['Precio'])

    # Almacenar los productos más económicos en el diccionario compartido
    # Only if actual value is worse than the new one
    if shared_dict.get('resolution_1', {}).get('Precio', '0') > resolution_1_min['Precio']:
        shared_dict['resolution_1'] = resolution_1_min
    if shared_dict.get('resolution_2', {}).get('Precio', '0') > resolution_2_min['Precio']:
        shared_dict['resolution_2'] = resolution_2_min
    if shared_dict.get('resolution_3', {}).get('Precio', '0') > resolution_3_min['Precio']:
        shared_dict['resolution_3'] = resolution_3_min


# Web driver para Chrome
def setup_driver():
    # Web driver para EDGE
    # s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
    # driver = webdriver.Edge(service=s)

    # Web driver para Chrome
    webdriver_path = 'C:/Users/Alejandro/chrome/chromedriver.exe'
    driver = webdriver.Chrome(webdriver_path)
    return driver


if __name__ == '__main__':
    # Crear un diccionario compartido para almacenar los resultados
    shared_data = multiprocessing.Manager().dict()

    # URLs a scrapear en Cyberpuerta
    cyberpuerta_urls = [
        'https://www.cyberpuerta.mx/Audio-y-Video/TV-y-Pantallas/Pantallas/Filtro/Tipo-HD/HD/',
        'https://www.cyberpuerta.mx/Pantallas-FullHD/',
        'https://www.cyberpuerta.mx/TV-4K-Ultra-HD/'
    ]

    process_cyberpuerta = multiprocessing.Process(target=scrape_cyberpuerta, args=(cyberpuerta_urls, shared_data, []))
    process_cyberpuerta.start()
    process_cyberpuerta.join()

    # Recuperar los resultados del diccionario compartido
    cyberpuerta_data = shared_data.get('cyberpuerta', [])

    # Crear un DataFrame con los datos de Cyberpuerta
    cyberpuerta_df = pd.DataFrame(cyberpuerta_data)

    # Guardar los datos en un archivo Excel
    cyberpuerta_df.to_excel('pantallas_cyberpuerta.xlsx', index=False)
