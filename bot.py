from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)  
# Función para iniciar sesión en Instagram
def login_instagram(email, password):
    print("Abriendo Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    try:
        print("Ingresando credenciales...")
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys(email)
        password_field.send_keys(password)

        print("Haciendo clic en 'Iniciar sesión'...")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(10)

        print("Login exitoso!")

    except Exception as e:
        print(f"Error durante el login: {e}")
        driver.quit()
        exit()


def go_to_profile():
    print("Navegando al perfil de 4GET...")
    driver.get("https://www.instagram.com/4getprods/")
    time.sleep(5)


def open_followers():
    try:
        print("Abriendo la lista de seguidores...")
        followers_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]")))
        followers_link.click()
        time.sleep(5)
    except Exception as e:
        print(f"Error al abrir seguidores: {e}")


def scroll_followers():
    print("Haciendo scroll en la lista de seguidores...")
    try:
        popup = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//ul")))
        for _ in range(5): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup)
            time.sleep(2)
    except Exception as e:
        print(f"Error al hacer scroll: {e}")

# Función para encontrar botones "Seguir"
def find_follow_buttons():
    try:
        buttons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//button[contains(., 'Seguir') and not(contains(., 'Siguiendo'))]")))
        return buttons
    except:
        return []

# Función para seguir usuarios en lotes de 5 con pausas de 5 minutos
def follow_users():
    followed_count = 0  

    while True:
        try:
            scroll_followers()  
            follow_buttons = find_follow_buttons()
            
            if not follow_buttons:
                print("No se encontraron más usuarios para seguir.")
                break

            for button in follow_buttons[:5]:  # Seguir solo a 5 personas en cada iteración
                driver.execute_script("arguments[0].click();", button)  
                followed_count += 1
                print(f"Seguido {followed_count} usuarios.")
                time.sleep(2)  #

            print("Esperando 5 minutos antes de seguir a más personas...")
            time.sleep(300)  # Pausa de 5 minutos 

        except Exception as e:
            print(f"Error al seguir usuarios: {e}")
            break

# **Ejecución del bot**
EMAIL = "martienezsofia21@gmail.com" 
PASSWORD = "Onlyghosttruch-02."      

login_instagram(EMAIL, PASSWORD)
go_to_profile()
open_followers()
follow_users()

# Cerrar el navegador
print("Cerrando el navegador...")
driver.quit()
