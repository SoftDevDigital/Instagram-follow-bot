from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import sqlite3

# Configuración del navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Función para iniciar sesión
def login_instagram(email, password):
    print("Abriendo Instagram...")
    driver.get("https://www.instagram.com")
    time.sleep(3)  # Esperar a que cargue la página

    try:
        print("Ingresando credenciales...")
        email_field = driver.find_element(By.NAME, "username")  # El campo sigue siendo "username" en el HTML
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys(email)  # Aquí pasamos el email
        password_field.send_keys(password)
        
        print("Haciendo clic en 'Iniciar sesión'...")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(7)  # Más tiempo para que cargue el dashboard

        # Saltar pop-ups posteriores
        try:
            print("Buscando botón 'Not Now' para guardar información...")
            not_now_button = driver.find_element(By.NAME, "_aaco")
            not_now_button.click()
            time.sleep(2)
        except:
            print("No se encontró el primer 'Not Now', continuando...")
            pass

        try:
            print("Buscando botón 'Not Now' para notificaciones...")
            not_now_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            not_now_button.click()
            time.sleep(2)
        except:
            print("No se encontró el segundo 'Not Now', continuando...")
            pass

    except Exception as e:
        print(f"Error durante el login: {e}")
        driver.quit()
        exit()

# Función para seguir cuentas por hashtag
def follow_accounts(hashtag, max_follows):
    print(f"Buscando cuentas con hashtag #{hashtag}...")
    conn = sqlite3.connect("seguimientos.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS follows 
                      (username TEXT, follow_date TEXT, followed_back INTEGER)''')

    driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
    time.sleep(50)

    posts = driver.find_elements(By.XPATH, "//article//a")
    followed_count = 0

    for post in posts:
        if followed_count >= max_follows:
            break

        try:
            post.click()
            time.sleep(2)
            username = driver.find_element(By.XPATH, "//header//a").text
            follow_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Follow')]")

            if follow_button:
                follow_button.click()
                cursor.execute("INSERT INTO follows VALUES (?, datetime('now'), 0)", (username,))
                conn.commit()
                followed_count += 1
                print(f"Seguido: {username}")
            driver.back()
            time.sleep(random.randint(10, 30))
        except Exception as e:
            print(f"Error al seguir una cuenta: {e}")
            driver.back()
            time.sleep(2)

    conn.close()

# Configuración inicial
EMAIL = "martienezsofia21@gmail.com"  # Reemplaza con tu correo
PASSWORD = "Onlyghosttruch-02."       # Reemplaza con tu contraseña
HASHTAG = "electronicmusic"
MAX_FOLLOWS = 10

# Ejecutar el bot
login_instagram(EMAIL, PASSWORD)
follow_accounts(HASHTAG, MAX_FOLLOWS)

# Cerrar el navegador
print("Cerrando el navegador...")
driver.quit()