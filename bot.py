from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
from collections import Counter
import traceback
import time
import random  # Importante para la aleatoriedad

# ================= CONFIGURACIÓN =================
EMAIL = "maildetesteo585@gmail.com"
PASSWORD = "Quelindorp2014"
TARGET_PROFILE = "https://www.instagram.com/4getprods/"
MAX_TOTAL_FOLLOWS = 200  # Límite máximo de personas a seguir

# Modo unfollow: usuario de **tu** cuenta (el que aparece en la URL del perfil)
MY_USERNAME = ""
MAX_TOTAL_UNFOLLOWS = 50
# Pausa entre cada dejar de seguir (segundos) — más corta que en follow para poder probar
UNFOLLOW_WAIT_MIN_SEC = 30
UNFOLLOW_WAIT_MAX_SEC = 90

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

def detect_username_from_nav():
    """Intenta obtener el @ desde enlaces del home (barra lateral / inferior)."""
    print("Detectando usuario desde la navegación...")
    driver.get("https://www.instagram.com/")
    wait_page_ready()
    time.sleep(random.uniform(2, 4))
    skip = {
        "", "explore", "reels", "accounts", "direct", "stories", "p", "tv", "legal",
        "about", "api", "www", "static", "help", "press", "jobs",
    }
    candidates = []
    for a in driver.find_elements(By.XPATH, "//a[@href]"):
        try:
            href = (a.get_attribute("href") or "").split("?")[0].rstrip("/")
            if "instagram.com/" not in href:
                continue
            tail = href.split("instagram.com/", 1)[-1]
            seg = tail.split("/")[0].lower()
            if not seg or seg in skip:
                continue
            if len(seg) > 30:
                continue
            if not seg.replace(".", "").replace("_", "").isalnum():
                continue
            candidates.append(seg)
        except Exception:
            pass
    if not candidates:
        return ""
    return Counter(candidates).most_common(1)[0][0]


def detect_username_from_settings():
    """Lee el @ desde Editar perfil cuando MY_USERNAME / --username están vacíos."""
    print("Detectando usuario de la sesión (editar perfil)...")
    driver.get("https://www.instagram.com/accounts/edit/")
    wait_page_ready()
    time.sleep(random.uniform(2, 4))
    inp = find_first_visible(
        [
            (By.NAME, "username"),
            (By.CSS_SELECTOR, "input[name='username']"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.XPATH, "//input[contains(@aria-label, 'usuario') or contains(@aria-label, 'username')]"),
        ],
        timeout=15,
    )
    if not inp:
        return ""
    try:
        val = inp.get_attribute("value") or ""
        return val.strip().rstrip("/")
    except Exception:
        return ""


def go_to_my_profile(username_override=None):
    u = (username_override or MY_USERNAME).strip().rstrip("/")
    if not u:
        u = detect_username_from_settings()
    if not u:
        u = detect_username_from_nav()
    if not u:
        raise ValueError(
            "No se pudo detectar el usuario. Configura MY_USERNAME o usa --username TU_USUARIO."
        )
    print(f"Usuario detectado/configurado: @{u}")
    url = f"https://www.instagram.com/{u}/"
    print(f"Yendo a tu perfil: {url}")
    driver.get(url)
    time.sleep(random.uniform(4, 6))

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

def get_siguiendo_buttons():
    """Botones 'Siguiendo' / 'Following' dentro del modal de lista de seguidos."""
    buttons = []
    for btn in driver.find_elements(By.XPATH, "//div[@role='dialog']//button"):
        try:
            t = btn.text.strip().lower()
            if t in ("siguiendo", "following"):
                buttons.append(btn)
        except Exception:
            pass
    return buttons

def confirm_unfollow_dialog():
    """Confirma el menú o modal tras pulsar Siguiendo."""
    time.sleep(random.uniform(0.4, 1.0))
    click_if_present(
        [
            "//button[contains(., 'Dejar de seguir')]",
            "//button[contains(., 'Unfollow')]",
            "//div[@role='dialog']//button[contains(., 'Dejar de seguir')]",
            "//span[contains(., 'Dejar de seguir')]/ancestor::button",
            "//span[contains(., 'Unfollow')]/ancestor::button",
        ],
        timeout=6,
    )

def run_unfollow_automation():
    total = 0
    while total < MAX_TOTAL_UNFOLLOWS:
        batch_size = random.randint(3, 8)
        print(f"\n--- Tanda unfollow. Objetivo en bloque: {batch_size} ---")

        n_batch = 0
        while n_batch < batch_size and total < MAX_TOTAL_UNFOLLOWS:
            btns = get_siguiendo_buttons()

            if not btns:
                print("No hay más 'Siguiendo'. Scrolleando la lista...")
                scroll_following()
                btns = get_siguiendo_buttons()
                if not btns:
                    print("Fin de la lista o UI distinta.")
                    break

            btn = btns[0]
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(random.uniform(0.8, 2.0))
                driver.execute_script("arguments[0].click();", btn)

                confirm_unfollow_dialog()

                total += 1
                n_batch += 1
                print(f"[{total}/{MAX_TOTAL_UNFOLLOWS}] Dejado de seguir.")

                wait_u = random.uniform(UNFOLLOW_WAIT_MIN_SEC, UNFOLLOW_WAIT_MAX_SEC)
                print(f"Esperando {wait_u:.1f} s antes del siguiente...")
                time.sleep(wait_u)
            except Exception as e:
                print(f"Error en unfollow: {e}")
                traceback.print_exc()
                break

        if total >= MAX_TOTAL_UNFOLLOWS:
            break
        print("Tanda unfollow terminada. Pausa...")
        time.sleep(random.randint(30, 60))


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
    parser = argparse.ArgumentParser(description="Bot Instagram: seguir o dejar de seguir desde listas.")
    parser.add_argument(
        "--mode",
        choices=("follow", "unfollow"),
        default="follow",
        help="follow = lista de seguidos del TARGET_PROFILE | unfollow = tu lista de seguidos",
    )
    parser.add_argument(
        "--username",
        default="",
        help="Tu usuario de Instagram (sin @), para unfollow. Si se omite, se usa MY_USERNAME en el script.",
    )
    parser.add_argument(
        "--max-unfollow",
        type=int,
        default=None,
        metavar="N",
        help="Solo unfollow: tope de cuentas (por defecto MAX_TOTAL_UNFOLLOWS en el script).",
    )
    args = parser.parse_args()

    if args.max_unfollow is not None:
        globals()["MAX_TOTAL_UNFOLLOWS"] = max(1, args.max_unfollow)

    try:
        login_instagram()

        if args.mode == "unfollow":
            go_to_my_profile(username_override=args.username or None)
            open_following()
            run_unfollow_automation()
        else:
            go_to_profile()
            open_following()
            run_automation()

    except Exception as e:
        print(f"\nHubo un problema: {e}")
        traceback.print_exc()
    finally:
        print("Proceso finalizado.")
        driver.quit()