import time
import random
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= CONFIGURACIÓN =================
EMAIL = "martienezsofia21@gmail.com"
PASSWORD = "Onlyghosttruch-02."
MY_PROFILE = "https://www.instagram.com/sofiimart20/"

def build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

driver = build_driver()

# ================= UTILIDADES =================

def find_element_safe(locator_list, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        for by, value in locator_list:
            try:
                el = driver.find_element(by, value)
                if el.is_displayed(): return el
            except: pass
        time.sleep(0.5)
    return None

# ================= LOGIN =================

def login_instagram():
    try:
        print(f"--- Abriendo Instagram para: {EMAIL} ---")
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(random.uniform(5, 7))
        
        user_input = find_element_safe([(By.NAME, "username"), (By.XPATH, "//input[@type='text']")])
        pass_input = find_element_safe([(By.NAME, "password"), (By.XPATH, "//input[@type='password']")])

        if user_input and pass_input:
            print("Introduciendo datos...")
            user_input.send_keys(EMAIL)
            time.sleep(1)
            pass_input.send_keys(PASSWORD)
            time.sleep(1)
            pass_input.send_keys(Keys.ENTER)
            
            print("Verificando acceso...")
            WebDriverWait(driver, 30).until(lambda d: "login" not in d.current_url)
            print("✅ ¡Login exitoso!")
            time.sleep(5)
            return True
        return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

# ================= EXTRACCIÓN SUPER ROBUSTA =================

def get_list_names(xpath_link, title_text):
    print(f"\n--- Extrayendo lista de {title_text} ---")
    names = set()
    try:
        driver.get(MY_PROFILE)
        time.sleep(6)
        
        # Click en Seguidores/Seguidos
        btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_link)))
        driver.execute_script("arguments[0].click();", btn)
        print(f"Abriendo ventana de {title_text}...")
        
        # ESPERA CRUCIAL: Esperamos a que aparezca cualquier diálogo
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        time.sleep(4) 

        # BUSCADOR DE MODAL (Nuevos selectores 2026)
        modal = None
        # Intentamos encontrar el div que tiene el scroll de varias formas
        modal_selectors = [
            "div._aano", 
            "div[role='dialog'] div.xyi19xy",
            "div[role='dialog'] div[style*='overflow-y: auto']",
            "div.x1n2onr6.x1vjfegm" # Clase detectada en perfiles nuevos
        ]
        
        for selector in modal_selectors:
            try:
                # Usamos un pequeño script para encontrar el que realmente tiene contenido
                temp = driver.execute_script(f"return document.querySelector('{selector}')")
                if temp:
                    modal = temp
                    print(f"✅ Contenedor detectado!")
                    break
            except: continue

        if not modal:
            # ÚLTIMO RECURSO: Intentar buscar por jerarquía si los nombres de clase fallan
            try:
                modal = driver.find_element(By.XPATH, "//div[@role='dialog']//div/div/div/div[3]")
                print("✅ Contenedor detectado por jerarquía!")
            except:
                print(f"❌ ERROR: No se pudo localizar el scroll de {title_text}.")
                return names

        last_h = 0
        iterations_stuck = 0
        
        while iterations_stuck < 5:
            # Capturar nombres: Buscamos links que estén dentro del diálogo
            # Filtramos para que solo traiga el texto del nombre de usuario
            elements = driver.find_elements(By.XPATH, "//div[@role='dialog']//a//span")
            
            for el in elements:
                try:
                    name = el.text.strip()
                    # Filtros para no agregar "Seguir", "Eliminar" o espacios vacíos
                    if name and len(name) > 1 and name not in ["Eliminar", "Seguir", "Siguiendo", "Verificado"]:
                        if "\n" not in name: # Los nombres de usuario no tienen saltos de línea
                            names.add(name)
                except: continue
            
            # Scroll usando JS
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(random.uniform(2.5, 3.5))
            
            new_h = driver.execute_script("return arguments[0].scrollHeight", modal)
            if new_h == last_h:
                iterations_stuck += 1
            else:
                iterations_stuck = 0
                last_h = new_h
            print(f"Buscando... {len(names)} usuarios detectados.")

        print(f"✅ Total final {title_text}: {len(names)}")
        return names
    except Exception as e:
        print(f"⚠️ Error en {title_text}: {e}")
        return names

def unfollow_process():
    # 1. Obtener Seguidores
    followers = get_list_names("//a[contains(@href, '/followers/')]", "Seguidores")
    time.sleep(4)
    # 2. Obtener Seguidos
    following = get_list_names("//a[contains(@href, '/following/')]", "Seguidos")

    if not followers or len(followers) < 1:
        print("\n❌ ABORTANDO: Lista de Seguidores vacía.")
        return

    # 3. Comparar
    to_unfollow = [u for u in following if u not in followers]
    print(f"\nGente que NO te sigue: {len(to_unfollow)}")

    # 4. Proceso de Unfollow Mejorado
    count = 0
    for user in to_unfollow:
        if count >= 10: break
        print(f"[{count+1}/10] Perfil: {user}")
        driver.get(f"https://www.instagram.com/{user}/")
        time.sleep(random.uniform(5, 7))
        
        try:
            # SELECTOR MEJORADO PARA EL BOTÓN "SIGUIENDO"
            # Buscamos el botón que CONTENGA un div con el texto
            btn = find_element_safe([
                (By.XPATH, "//button[.//div[text()='Siguiendo' or text()='Following']]"),
                (By.XPATH, "//button[contains(., 'Siguiendo')]"),
                (By.XPATH, "//header//button[div]") # Tercer recurso: el botón principal del header
            ])
            
            if btn:
                # Usamos JavaScript para el clic, es más efectivo contra capas invisibles
                driver.execute_script("arguments[0].click();", btn)
                print("Click en 'Siguiendo'...")
                time.sleep(3)
                
                # MODAL DE CONFIRMACIÓN (Aquí es donde se suele trabar)
                confirmar = find_element_safe([
                    (By.XPATH, "//button[text()='Dejar de seguir' or text()='Unfollow']"),
                    (By.XPATH, "//div[@role='dialog']//button[contains(., 'Dejar de seguir')]"),
                    (By.XPATH, "//button[contains(@class, '_a9--') and contains(@class, '_a9-_')]") # Botón rojo
                ])
                
                if confirmar:
                    driver.execute_script("arguments[0].click();", confirmar)
                    print(f"✅ ¡Éxito! Dejaste de seguir a {user}")
                    count += 1
                    # Pausa aleatoria para que Instagram no sospeche
                    espera = random.uniform(45, 70)
                    print(f"Esperando {int(espera)} segundos para el próximo...")
                    time.sleep(espera)
                else:
                    print(f"⚠️ No apareció el modal de confirmación para {user}")
            else:
                print(f"⚠️ No se encontró el botón 'Siguiendo' en el perfil de {user}")
        except Exception as e:
            print(f"❌ Error al procesar a {user}: {e}")
            
if __name__ == "__main__":
    try:
        if login_instagram():
            unfollow_process()
    finally:
        print("\n--- Tarea finalizada ---")
        driver.quit()