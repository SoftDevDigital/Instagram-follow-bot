from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configura el servicio con ChromeDriverManager
service = Service(ChromeDriverManager().install())

# Inicializa el navegador Chrome con el servicio
driver = webdriver.Chrome(service=service)

# Abre una página para probar
driver.get("https://www.google.com")

# Cierra el navegador
driver.quit()