import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    # Web driver para EDGE
    # s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
    # driver = webdriver.Edge(service=s)

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


# Define la función para extraer la resolución del título
def extract_resolution(title):
    if "4K" in title or "UHD" in title or "3840" in title:
        return "4K UHD 3840 x 2160"
    elif "FHD" in title or "1920" in title:
        return "FHD 1920 x 1080"
    elif "HD" in title or "1366" in title:
        return "HD 1366 x 768"
    else:
        return "FHD 1920 x 1080"


def scrape_soriana(URL):
    driver = setup_driver()
    # Abre la URL
    driver.get(URL)
    wait = WebDriverWait(driver, 10)

    # Desplazarse por la página para asegurar que se cargan todos los productos
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Esperar hasta que los productos se carguen después de desplazarse
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.product-tile--wrapper')))

    # Analizar el contenido de la página con BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    productos = soup.select('div.product-tile--wrapper')

    data = []
    for producto in productos:
        try:
            titulo = producto.select_one('a.product-tile--link').get_text(strip=True)
            precio = producto.select_one('span.price-plp').get_text(strip=True)
            url_imagen = producto.select_one('img.tile-image')['src'].strip()
            resolucion = extract_resolution(titulo)
            # Añade la información del producto a la lista
            data.append({
                'Titulo': titulo,
                'Precio': precio,
                'Resolución': resolucion,
                'URL Imagen': url_imagen,
                'Tienda': 'Soriana'
            })
        except Exception as e:
            print(f"Error al procesar un producto: {e}")
    # Cerrar el WebDriver
    driver.quit()
    return data


# URLs a scrapear
urls = [
    'https://www.soriana.com/buscar?q=pantalla+hd&search-button=',
    'https://www.soriana.com/buscar?q=Pantalla+JVC+43+Pulg+Roku+Framless&search-button=',
    'https://www.soriana.com/buscar?q=Pantalla+4k&search-button='
]

# DataFrame para recopilar los datos de todas las URLs
all_tvs = pd.DataFrame()

for url in urls:
    # Scrapear cada URL y añadir los datos al DataFrame
    tvs_data = scrape_soriana(url)
    all_tvs = pd.concat([all_tvs, pd.DataFrame(tvs_data)], ignore_index=True)

# Guardar los datos en un archivo Excel
all_tvs.to_excel('pantallas_soriana.xlsx', index=False)
