import re

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def setup_driver():
    # Web driver para EDGE
    # s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
    # driver = webdriver.Edge(service=s)
    # Define los headers para el request HTTP
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    # }

    # Web driver para Chrome
    webdriver_path = 'C:/Users/Alejandro/chrome/chromedriver.exe'
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(webdriver_path, options=options)
    return driver


def scrape_pcel(urls):
    monitors = []
    regex = re.compile(
        r"(?P<tipo>[\w\s]+)\sde\s(?P<pulgadas>\d+(\.\d+)?\")?.*?Resolución\s*(?P<resolucion>[\d\sx]+)?.*?(?P<ms>\d+\sms)?")

    for base_url in urls:
        driver = setup_driver()
        # Abre la URL
        driver.get(base_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        next_page = True
        while next_page:
            monitor_elements = soup.find_all('div', class_='name')
            for monitor_element in monitor_elements:
                description = monitor_element.a.text
                match = regex.search(description)
                if match:
                    price_div = monitor_element.find_next('div', class_='price')
                    price = price_div.text.strip() if price_div else 'No disponible'

                    # Buscar el elemento de imagen al mismo nivel que el elemento de nombre
                    image_div = monitor_element.find_next('div', class_='image')
                    image_url = image_div.find('img')['src'] if image_div else 'No disponible'

                    monitor_info = match.groupdict()
                    monitor_info['Precio'] = price
                    monitor_info['URL Imagen'] = image_url
                    monitor_info['Tienda'] = 'PCEL'
                    monitors.append(monitor_info)

            # Busca si hay una página siguiente
            next_li_element = soup.find('li', class_='next')
            if next_li_element and next_li_element.find('a'):
                next_page_url = next_li_element.find('a', href=True)['href']
                driver.get(base_url + next_page_url)
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
            else:
                next_page = False

        driver.quit()
    return monitors


# URLs a scrapear en PCEL
pcel_urls = [
    'https://pcel.com/index.php?route=product/search&filter_name=televisión 1366',
    'https://pcel.com/index.php?route=product/search&filter_name=televisión 1920',
    'https://pcel.com/index.php?route=product/search&filter_name=Televisi%C3%B3n%203840'
]

# Obtener los datos de PCEL
pcel_data = scrape_pcel(pcel_urls)

# Crear un DataFrame para los datos de PCEL
pcel_df = pd.DataFrame(pcel_data)

# Guardar los datos en un archivo Excel
pcel_df.to_excel('pantallas_pcel.xlsx', index=False)
