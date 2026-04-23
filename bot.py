from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import time
import random  # Importante para la aleatoriedad

# ================= CONFIGURACIÓN =================
EMAIL = "maildetesteo585@gmail.com"
PASSWORD = "Quelindorp2014"
TARGET_PROFILE = "https://www.instagram.com/4getprods/"
MAX_TOTAL_FOLLOWS = 200 # Límite máximo de personas a seguir

def build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=es-ES")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

driver = build_driver()
wait = WebDriverWait(driver, 30)

# ================= UTILIDADES =================
def click_if_present(xpaths, timeout=4):
    for xpath in xpaths:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            return True
        except:
            pass
    return False

def wait_page_ready():
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def find_first_visible(locator_list, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        for by, value in locator_list:
            try:
                elements = driver.find_elements(by, value)
                for el in elements:
                    if el.is_displayed():
                        return el
            except:
                pass
        time.sleep(0.5)
    return None

# ================= LOGIN =================
def login_instagram():
    print("Abriendo Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    wait_page_ready()
    time.sleep(random.uniform(3, 5))

    try:
        click_if_present([
            "//button[contains(., 'Permitir')]",
            "//button[contains(., 'Allow')]",
            "//button[contains(., 'Aceptar')]",
        ], timeout=6)

        username = find_first_visible([(By.NAME, "username"), (By.CSS_SELECTOR, "input[type='text']")])
        password = find_first_visible([(By.NAME, "password"), (By.CSS_SELECTOR, "input[type='password']")])

        for char in EMAIL:
            username.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        for char in PASSWORD:
            password.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

        time.sleep(1)
        password.send_keys(Keys.ENTER)

        WebDriverWait(driver, 20).until(lambda d: "/accounts/login" not in d.current_url)
        time.sleep(random.uniform(4, 6))
        
        click_if_present(["//button[contains(., 'Ahora no')]", "//button[contains(., 'Not now')]"], timeout=8)
        print("Login OK")
    except Exception as e:
        print("Error login:", e)
        driver.quit()
        exit()

# ================= NAVEGACIÓN =================
def go_to_profile():
    print(f"Yendo al perfil objetivo: {TARGET_PROFILE}")
    driver.get(TARGET_PROFILE)
    time.sleep(random.uniform(4, 6))

def open_following():
    print("Abriendo lista de seguidos...")
    link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following/')]")))
    driver.execute_script("arguments[0].click();", link)
    time.sleep(random.uniform(3, 5))

def scroll_following():
    try:
        modal = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[contains(@class, 'xyi19xy')]")))
    except:
        modal = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
    
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", modal)
    time.sleep(random.uniform(2, 4))

# ================= ACCIÓN DE SEGUIR =================
def get_follow_buttons():
    buttons = []
    for btn in driver.find_elements(By.XPATH, "//button"):
        try:
            if btn.text.strip().lower() == "seguir":
                buttons.append(btn)
        except:
            pass
    return buttons

def run_automation():
    total_followed = 0
    
    while total_followed < MAX_TOTAL_FOLLOWS:
        # Definir cuántas personas seguir en esta tanda
        batch_size = random.randint(5, 10)
        print(f"\n--- Iniciando nueva tanda. Objetivo: {batch_size} personas ---")
        
        followed_in_batch = 0
        
        while followed_in_batch < batch_size and total_followed < MAX_TOTAL_FOLLOWS:
            buttons = get_follow_buttons()
            
            if not buttons:
                print("No hay más botones de 'Seguir'. Scrolleando...")
                scroll_following()
                buttons = get_follow_buttons()
                if not buttons: break

            btn = buttons[0]
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(random.uniform(1, 3))
                
                driver.execute_script("arguments[0].click();", btn)
                
                total_followed += 1
                followed_in_batch += 1
                print(f"[{total_followed}/{MAX_TOTAL_FOLLOWS}] Siguiendo...")

                # --- CAMBIO SOLICITADO AQUÍ ---
                # 300,000ms a 600,000ms son 300 a 600 segundos
                wait_time = random.uniform(300, 600) 
                print(f"Esperando {wait_time:.2f} segundos (entre 5 y 10 min) para el siguiente...")
                time.sleep(wait_time)
                # ------------------------------
                
            except Exception as e:
                print(f"Error al clickear: {e}")
                break

        if total_followed >= MAX_TOTAL_FOLLOWS:
            break

        # Pausa extra entre tandas (opcional, ya que la pausa individual ya es muy larga)
        print("Tanda finalizada. Tomando un respiro extra...")
        time.sleep(random.randint(60, 120)) 


# ================= MAIN =================
if __name__ == "__main__":
    try:
        login_instagram()
        go_to_profile()
        open_following()
        
        # Ejecutar la lógica de tandas y tiempos aleatorios
        run_automation()

    except Exception as e:
        print(f"\nHubo un problema: {e}")
        traceback.print_exc()
    finally:
        print("Proceso finalizado.")
        driver.quit()