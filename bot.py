from instagrapi import Client
import time
import random

# Configurar el cliente de Instagram
cl = Client()
EMAIL = "martienezsofia21@gmail.com"
PASSWORD = "Onlyghosttruch-02."

# Función para iniciar sesión en Instagram
def login_instagram(email, password):
    print("Iniciando sesión en Instagram...")
    try:
        cl.login(email, password)
        print("Login exitoso!")
    except Exception as e:
        print(f"Error durante el login: {e}")
        exit()

# Función para seguir usuarios de un perfil objetivo
def follow_users(target_username, max_follows=5):
    print(f"Navegando a los seguidores de {target_username}...")
    try:
        target_user_id = cl.user_id_from_username(target_username)
        followers = cl.user_followers(target_user_id, amount=50)  # Obtener hasta 50 seguidores

        followed_count = 0
        for user_id in followers:
            if followed_count >= max_follows:
                break
            try:
                cl.user_follow(user_id)
                username = followers[user_id].username
                followed_count += 1
                print(f"Seguido usuario #{followed_count}: {username}")
                time.sleep(random.uniform(2, 5))  # Pausa aleatoria
            except Exception as e:
                print(f"Error al seguir a {followers[user_id].username}: {e}")
                time.sleep(10)

        if followed_count > 0:
            print(f"Seguido {followed_count} usuarios. Esperando 2 minutos...")
            time.sleep(120)  # Pausa de 2 minutos como en el original
        else:
            print("No se encontraron usuarios para seguir.")
    except Exception as e:
        print(f"Error al obtener seguidores de {target_username}: {e}")

# Función para dejar de seguir a quienes no te siguen
def dejar_de_seguir(my_username):
    print("Analizando seguidos y seguidores...")
    try:
        my_user_id = cl.user_id_from_username(my_username)
        
        # Obtener lista de seguidos
        following = cl.user_following(my_user_id, amount=0)  # 0 = todos
        following_usernames = {cl.username_from_user_id(user_id) for user_id in following}
        print(f"Total de seguidos: {len(following_usernames)}")

        # Obtener lista de seguidores
        followers = cl.user_followers(my_user_id, amount=0)
        followers_usernames = {cl.username_from_user_id(user_id) for user_id in followers}
        print(f"Total de seguidores: {len(followers_usernames)}")

        # Calcular quiénes no te siguen de vuelta
        no_me_siguen = following_usernames - followers_usernames
        print(f"Personas que no te siguen de vuelta: {len(no_me_siguen)}")

        # Dejar de seguir
        for username in no_me_siguen:
            try:
                user_id = cl.user_id_from_username(username)
                cl.user_unfollow(user_id)
                print(f"Has dejado de seguir a {username}")
                time.sleep(random.uniform(5, 10))  # Pausa aleatoria para evitar detección
            except Exception as e:
                print(f"Error al dejar de seguir a {username}: {e}")
                time.sleep(10)
    except Exception as e:
        print(f"Error al analizar listas: {e}")

# **Ejecución del bot**
login_instagram(EMAIL, PASSWORD)
follow_users("4getprods")  # Seguir usuarios de "4getprods"
dejar_de_seguir("sofiimart20")  # Dejar de seguir desde tu cuenta

print("Bot finalizado.")