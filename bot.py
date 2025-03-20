from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import logging
import smtplib
from email.mime.text import MIMEText

# Configuración de logging
logging.basicConfig(filename='bot_activity.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Cargar configuración
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Archivo config.json no encontrado. Usa valores predeterminados.")
        return {
            "email": "martienezsofia21@gmail.com",
            "password": "Onlyghosttruch-02.",
            "target_accounts": ["alexander.ac026", "otra_cuenta_musical"],
            "max_follows_per_account": 50,
            "notification_email": "tu_correo@outlook.com",
            "smtp_email": "tu_correo@outlook.com",
            "smtp_password": "tu_contraseña_normal"
        }

# Cargar estado
def load_state():
    try:
        with open("bot_state.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_target": "", "followed_count": 0, "unfollowed_count": 0}

def save_state(last_target, followed_count, unfollowed_count):
    with open("bot_state.json", "w") as f:
        json.dump({"last_target": last_target, "followed_count": followed_count, "unfollowed_count": unfollowed_count}, f)

def generate_report(followed, unfollowed):
    with open("report.txt", "w") as f:
        f.write(f"Usuarios seguidos: {followed}\n")
        f.write(f"Usuarios dejados de seguir: {unfollowed}\n")
        f.write(f"Fecha: {time.ctime()}\n")
    logging.info("Reporte generado en report.txt")

# Enviar notificación por correo y detener el bot (usando Outlook SMTP)
def send_notification_email_and_stop(config, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = 'Bot de Instagram: Sin usuarios para seguir - Detenido'
        msg['From'] = config["smtp_email"]
        msg['To'] = config["notification_email"]

        # Usar el servidor SMTP de Outlook
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
            server.starttls()  # Activar TLS
            server.login(config["smtp_email"], config["smtp_password"])  # Usar contraseña normal
            server.send_message(msg)
        logging.info("Notificación enviada por correo. Deteniendo el bot...")
    except Exception as e:
        logging.error(f"Error al enviar notificación por correo: {e}")
    finally:
        driver.quit()
        exit()

# Configuración del navegador (local)
config = load_config()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

def login_instagram(email, password, retries=3):
    for attempt in range(retries):
        try:
            logging.info("Abriendo Instagram...")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            email_field.send_keys(email)
            password_field.send_keys(password)
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(10)
            if "challenge" in driver.current_url:
                logging.warning("Se detectó un CAPTCHA. Resuelve manualmente y presiona Enter...")
                input()
            else:
                logging.info("Login exitoso!")
                return True
        except Exception as e:
            logging.error(f"Intento {attempt + 1} fallido: {e}")
            time.sleep(10)
    logging.error("No se pudo iniciar sesión tras varios intentos.")
    driver.quit()
    exit()

def go_to_profile(username):
    logging.info(f"Navegando al perfil de {username}...")
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

def open_followers():
    try:
        logging.info("Abriendo la lista de seguidores...")
        followers_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]")))
        followers_link.click()
        time.sleep(5)
    except Exception as e:
        logging.error(f"Error al abrir seguidores: {e}")

def scroll_followers():
    try:
        popup = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//ul")))
        last_height = driver.execute_script("return arguments[0].scrollHeight", popup)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup)
            time.sleep(random.uniform(2, 4))
            new_height = driver.execute_script("return arguments[0].scrollHeight", popup)
            if new_height == last_height:
                logging.info("No se cargaron más seguidores.")
                break
            last_height = new_height
    except Exception as e:
        logging.error(f"Error al hacer scroll: {e}")

def find_follow_buttons():
    try:
        buttons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//button[contains(., 'Seguir') and not(contains(., 'Siguiendo'))]")))
        return buttons
    except:
        return []

def save_followed_users(username):
    with open("followed_users.json", "a") as f:
        json.dump({"username": username, "date": time.ctime()}, f)
        f.write("\n")

def follow_users(max_follows):
    followed_count = 0
    while followed_count < max_follows:
        try:
            scroll_followers()
            follow_buttons = find_follow_buttons()
            if not follow_buttons:
                logging.info("No se encontraron más usuarios para seguir en esta cuenta.")
                return followed_count, True
            for button in follow_buttons[:5]:
                driver.execute_script("arguments[0].click();", button)
                followed_count += 1
                username = button.find_element(By.XPATH, "./ancestor::div//a").text
                save_followed_users(username)
                logging.info(f"Seguido {followed_count} usuarios: {username}")
                time.sleep(random.uniform(2, 5))
                if followed_count >= max_follows:
                    logging.info(f"Límite de {max_follows} usuarios alcanzado.")
                    return followed_count, False
            time.sleep(random.uniform(300, 360))
        except Exception as e:
            logging.error(f"Error al seguir usuarios: {e}")
            break
    return followed_count, False

def open_following():
    try:
        logging.info("Abriendo la lista de 'Siguiendo'...")
        driver.get(f"https://www.instagram.com/{config['email'].split('@')[0]}/")
        time.sleep(5)
        following_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following/')]")))
        following_link.click()
        time.sleep(5)
    except Exception as e:
        logging.error(f"Error al abrir 'Siguiendo': {e}")

def unfollow_users(limit):
    unfollowed_count = 0
    try:
        scroll_followers()
        unfollow_buttons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//button[contains(., 'Siguiendo')]")))
        for button in unfollow_buttons[:limit]:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
            confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Dejar de seguir')]")))
            confirm_button.click()
            unfollowed_count += 1
            logging.info(f"Dejado de seguir a {unfollowed_count} usuarios.")
            time.sleep(random.uniform(2, 5))
        time.sleep(random.uniform(300, 360))
    except Exception as e:
        logging.error(f"Error al dejar de seguir: {e}")
    return unfollowed_count

if __name__ == "__main__":
    state = load_state()
    total_followed = state["followed_count"]
    total_unfollowed = state["unfollowed_count"]
    all_targets_exhausted = True

    if login_instagram(config["email"], config["password"]):
        for target in config["target_accounts"]:
            if target <= state["last_target"]:
                continue
            go_to_profile(target)
            open_followers()
            followed_in_run, exhausted = follow_users(config["max_follows_per_account"])
            total_followed += followed_in_run
            save_state(target, total_followed, total_unfollowed)
            if not exhausted:
                all_targets_exhausted = False

        if all_targets_exhausted and state["last_target"] == config["target_accounts"][-1]:
            message = "El bot ha procesado todas las cuentas objetivo y no hay más usuarios para seguir.\n" \
                      "Por favor, actualiza 'target_accounts' en config.json y reinicia el bot."
            send_notification_email_and_stop(config, message)

        # Opcional: Dejar de seguir
        # open_following()
        # unfollowed_in_run = unfollow_users(limit=10)
        # total_unfollowed += unfollowed_in_run
        # save_state(config["target_accounts"][-1], total_followed, total_unfollowed)

    generate_report(total_followed, total_unfollowed)
    logging.info("Cerrando el navegador...")
    driver.quit()
    