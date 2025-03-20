Aquí tienes un `README.md` detallado en formato Markdown que explica qué hace el bot hasta ahora, cómo funciona, cómo configurarlo y cómo ejecutarlo. Este README está diseñado para ser claro tanto para ti como para cualquier otra persona que pueda usarlo en el futuro. Incluye todas las funcionalidades implementadas y las instrucciones necesarias.

---

```markdown
# Instagram Automation Bot

Este proyecto es un bot automatizado para Instagram construido con Python y Selenium. Su objetivo principal es aumentar la interacción y el crecimiento de una cuenta de Instagram mediante la automatización de acciones como seguir usuarios, dejar de seguir, dar "Me gusta", comentar publicaciones y reaccionar a historias, todo mientras mantiene un enfoque seguro para evitar detecciones o bloqueos por parte de Instagram.

## Características principales

El bot está diseñado para ejecutar las siguientes acciones desde una cuenta principal, con un enfoque en estrategias de crecimiento orgánico:

1. **Seguir usuarios objetivo**  
   - Sigue a los seguidores de cuentas específicas (ej. `4getprods`) o usuarios que publican bajo hashtags relevantes (ej. `#musicproducer`).
   - Filtra usuarios antes de seguirlos según criterios como publicaciones mínimas, número de seguidores y si son cuentas privadas o spam.

2. **Dejar de seguir automáticamente**  
   - Deja de seguir a usuarios que no devuelven el follow después de 2 días.
   - Respeta una lista blanca (whitelist) de usuarios que nunca serán dejados de seguir.

3. **Automatización de interacciones**  
   - Da "Me gusta" a publicaciones recientes de cuentas objetivo o propias.
   - Deja comentarios personalizados (ej. "¡Gran contenido!") en publicaciones.
   - Envía reacciones (emojis) a las historias de los usuarios seguidos.

4. **Gestión inteligente**  
   - Rota entre múltiples cuentas objetivo para diversificar la fuente de seguidores.
   - Ejecuta acciones en horarios específicos (8 AM, 12 PM, 6 PM, 10 PM) para simular comportamiento humano.
   - Ajusta límites diarios de follows/unfollows según la antigüedad de la cuenta.

5. **Seguridad y monitoreo**  
   - Usa pausas aleatorias (2-4 segundos entre acciones, 5-10 minutos entre lotes) para evitar detección.
   - Pausa por 24 horas si detecta un mensaje de "acción bloqueada" de Instagram.
   - Genera reportes de estadísticas (follows, unfollows, likes, etc.) y logs de actividad.

## Requisitos

- **Python 3.8+**
- **Dependencias**: Instala las siguientes librerías con `pip`:
  ```bash
  pip install selenium webdriver-manager
  ```
- **Google Chrome**: Debe estar instalado en el sistema.
- **ChromeDriver**: Gestionado automáticamente por `webdriver-manager`.

## Configuración

1. **Clonar o descargar el repositorio**  
   Guarda el archivo `instagram_bot.py` en tu máquina.

2. **Configurar credenciales**  
   Edita las siguientes variables al final del archivo:
   ```python
   EMAIL = "tu_correo@gmail.com"  # Tu email de Instagram
   PASSWORD = "tu_contraseña"     # Tu contraseña de Instagram
   MY_USERNAME = "tu_usuario"     # Tu nombre de usuario de Instagram
   TARGET_ACCOUNTS = ["cuenta1", "cuenta2"]  # Cuentas de las que seguir seguidores
   HASHTAGS = ["hashtag1", "hashtag2"]       # Hashtags para buscar usuarios
   COMMENTS_LIST = ["¡Gran contenido!", "Sigue así!"]  # Lista de comentarios
   ```

3. **Archivos generados**  
   El bot creará automáticamente estos archivos en el directorio:
   - `followed_users.json`: Rastrea a quién sigues y cuándo.
   - `whitelist.json`: Lista de usuarios que no serán dejados de seguir (edítalo manualmente si es necesario).
   - `bot_stats.json`: Estadísticas de acciones realizadas.
   - `bot_logs.txt`: Registro de actividad.

## Uso

### Ejecución local
1. Asegúrate de tener las dependencias instaladas.
2. Ejecuta el script:
   ```bash
   python instagram_bot.py
   ```
3. El bot iniciará sesión y comenzará a ejecutar las acciones programadas en un bucle continuo.

### Ejecución en servidor (24/7)
Para mantener el bot activo 24/7, despliega en un VPS (como Hostinger, DigitalOcean o AWS):
1. Configura el VPS con Ubuntu y sube el archivo.
2. Instala dependencias:
   ```bash
   sudo apt update && sudo apt install python3-pip google-chrome-stable -y
   pip3 install selenium webdriver-manager
   ```
3. Usa `PM2` para ejecutarlo como proceso en segundo plano:
   ```bash
   sudo npm install -g pm2
   pm2 start instagram_bot.py --interpreter python3
   pm2 save
   pm2 startup
   ```

### Modo headless
El bot está configurado por defecto en modo `headless` (sin interfaz gráfica). Para verlo en acción localmente, comenta estas líneas en `options`:
```python
# options.add_argument("--headless")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
```

## Funcionalidades detalladas

### 1. Seguir usuarios
- **Desde cuentas objetivo**: Sigue a los seguidores de las cuentas en `TARGET_ACCOUNTS`.
- **Por hashtags**: Busca publicaciones en `HASHTAGS` y sigue a los autores.
- **Filtro**: Solo sigue usuarios con al menos 5 publicaciones, 50 seguidores, no privados y sin patrones de spam.

### 2. Dejar de seguir
- Revisa `followed_users.json` y deja de seguir a quienes no devolvieron el follow tras 2 días.
- Respeta `whitelist.json` para excepciones.

### 3. Interacciones
- **Likes**: Da "Me gusta" a hasta 3 publicaciones por cuenta objetivo o propias.
- **Comentarios**: Publica un comentario aleatorio de `COMMENTS_LIST` en hasta 1 publicación por cuenta.
- **Historias**: Envía reacciones (🔥, 👏, ❤️) a hasta 5 historias de tu perfil.

### 4. Seguridad
- Pausas: 2-4 segundos entre acciones, 5-10 minutos entre lotes, 1 hora entre ciclos completos.
- Pausa prolongada: 24 horas si detecta bloqueo.
- Límite diario: 150 follows/unfollows por defecto (ajustable en `bot_stats.json`).

### 5. Reportes
- Estadísticas en `bot_stats.json`: follows, unfollows, likes, comments, story_reactions.
- Logs en `bot_logs.txt`: Registro de cada acción con timestamp.

## Personalización

- **Ajustar límites**: Modifica `max_follows`, `batch_size`, o `daily_follow_limit` en el código o en `bot_stats.json`.
- **Cambiar horarios**: Edita la lista `[8, 12, 18, 22]` en `run_bot` para otros horarios.
- **Agregar a whitelist**: Edita manualmente `whitelist.json` con usernames.

## Advertencias

- **Riesgo de bloqueo**: Instagram puede bloquear cuentas que usen bots. Usa con moderación y prueba con una cuenta secundaria primero.
- **Proxies**: Considera usar un proxy en el VPS para rotar IPs si planeas escalar.
- **Límites seguros**: No excedas 200-300 acciones diarias en cuentas nuevas, o 400-500 en cuentas antiguas.

## Contribuciones

Si deseas agregar funcionalidades o reportar errores, abre un issue o envía un pull request en el repositorio (si lo subes a GitHub).

## Licencia

Este proyecto es de uso libre para fines personales. No me hago responsable por el uso indebido o consecuencias en tu cuenta de Instagram.
```

---

### Notas sobre el README
- **Estructura clara**: Explica qué hace el bot, cómo instalarlo, configurarlo y ejecutarlo.
- **Instrucciones específicas**: Incluye pasos para uso local y en servidor, con comandos exactos.
- **Advertencias**: Resalta los riesgos para que estés informado.
- **Personalización**: Detalla cómo ajustar parámetros clave.

Este README refleja el estado actual del bot con todas las 15 funcionalidades implementadas. Si quieres que lo ajuste (por ejemplo, agregar más detalles técnicos o simplificarlo), solo dime. ¿Te parece bien así? ¿Seguimos con algo más?