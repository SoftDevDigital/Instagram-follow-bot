from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configurar el driver
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# Función para iniciar sesión en Instagram
def login_instagram(email, password):
    print("Abriendo Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    try:
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        email_field.send_keys(email)
        password_field.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(10)
        print("Login exitoso!")
    except Exception as e:
        print(f"Error durante el login: {e}")
        driver.quit()
        exit()

# Navegar al perfil específico
def go_to_profile(username):
    print(f"Navegando al perfil de {username}...")
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

# Abrir la lista de seguidores o seguidos
def open_list(tipo):
    try:
        print(f"Abriendo la lista de {tipo}...")
        list_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{tipo}/')]")))
        list_link.click()
        time.sleep(5)
    except Exception as e:
        print(f"Error al abrir la lista de {tipo}: {e}")

# Obtener lista de seguidores o seguidos
def obtener_lista(tipo):
    print(f"Obteniendo la lista de {tipo}...")
    nombres = set()
    try:
        popup = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//ul")))
        for _ in range(10):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup)
            time.sleep(2)
        
        elementos = driver.find_elements(By.XPATH, "//a[contains(@href, '/')]//span")
        for elem in elementos:
            nombres.add(elem.text)
    except Exception as e:
        print(f"Error al obtener la lista de {tipo}: {e}")
    return nombres

# Función para encontrar botones "Seguir"
def find_follow_buttons():
    try:
        buttons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//button[contains(., 'Seguir') and not(contains(., 'Siguiendo'))]")))
        return buttons
    except:
        return []

# Función para seguir usuarios en lotes de 5
def follow_users():
    followed_count = 0
    while True:
        try:
            follow_buttons = find_follow_buttons()
            if not follow_buttons:
                print("No se encontraron más usuarios para seguir.")
                break

            for button in follow_buttons[:5]:
                driver.execute_script("arguments[0].click();", button)
                followed_count += 1
                print(f"Seguido {followed_count} usuarios.")
                time.sleep(2)

            print("Esperando 2 minutos antes de seguir a más personas...")
            time.sleep(120)  # Pausa de 2 minutos (120 segundos)
            break  # Se sigue solo a 5 personas y se detiene

        except Exception as e:
            print(f"Error al seguir usuarios: {e}")
            break

# Función para dejar de seguir a quienes no te siguen
def dejar_de_seguir():
    go_to_profile("sofiimart20")  # Ir a tu perfil
    open_list("following")  # Abrir seguidos
    seguidos = obtener_lista("following")

    open_list("followers")  # Abrir seguidores
    seguidores = obtener_lista("followers")

    no_me_siguen = seguidos - seguidores
    print(f"Personas que no te siguen de vuelta: {len(no_me_siguen)}")

    for usuario in no_me_siguen:
        try:
            driver.get(f"https://www.instagram.com/{usuario}/")
            time.sleep(5)
            boton_dejar_de_seguir = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Siguiendo')]")))
            boton_dejar_de_seguir.click()
            time.sleep(2)
            confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Dejar de seguir')]")))
            confirmar.click()
            print(f"Has dejado de seguir a {usuario}")
            time.sleep(3)
        except Exception as e:
            print(f"Error al dejar de seguir a {usuario}: {e}")
            continue

# **Ejecución del bot**
EMAIL = "martienezsofia21@gmail.com"
PASSWORD = "Onlyghosttruch-02."

login_instagram(EMAIL, PASSWORD)
go_to_profile("4getprods")
open_list("followers")
follow_users()
dejar_de_seguir()

# Cerrar el navegador
print("Cerrando el navegador...")
driver.quit()
