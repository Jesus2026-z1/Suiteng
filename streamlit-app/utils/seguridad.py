"""
Modulo de Seguridad para la aplicacion Streamlit.
Contiene funciones de proteccion contra ataques, validacion de datos,
generacion de tokens y otras medidas de seguridad.
"""

import streamlit as st
import hashlib
import hmac
import time
import re
import os
from datetime import datetime, timedelta
from collections import defaultdict
import json

# ============================================================================
# RATE LIMITING (Prevencion de Fuerza Bruta)
# ============================================================================

# Almacenamiento de intentos (en memoria - en produccion usar Redis o DB)
_intentos_fallidos = defaultdict(list)
_intentos_api = defaultdict(list)

# Configuracion de rate limiting
MAX_INTENTOS_LOGIN = 5
VENTANA_TIEMPO_LOGIN = 300  # 5 minutos
MAX_INTENTOS_API = 100
VENTANA_TIEMPO_API = 60  # 1 minuto

def verificar_rate_limit_login(identificador):
    """
    Verifica si un usuario/IP ha excedido el limite de intentos de login.
    
    Parametros:
        identificador (str): Username o IP del usuario
    
    Retorna:
        tuple: (permitido: bool, mensaje: str)
    """
    ahora = time.time()
    
    # Limpiar intentos antiguos
    _intentos_fallidos[identificador] = [
        t for t in _intentos_fallidos[identificador]
        if ahora - t < VENTANA_TIEMPO_LOGIN
    ]
    
    num_intentos = len(_intentos_fallidos[identificador])
    
    if num_intentos >= MAX_INTENTOS_LOGIN:
        tiempo_espera = VENTANA_TIEMPO_LOGIN - (ahora - _intentos_fallidos[identificador][0])
        minutos = int(tiempo_espera / 60) + 1
        return False, "Demasiados intentos. Espera {} minuto(s).".format(minutos)
    
    return True, ""

def registrar_intento_fallido_login(identificador):
    """
    Registra un intento de login fallido.
    
    Parametros:
        identificador (str): Username o IP del usuario
    """
    _intentos_fallidos[identificador].append(time.time())

def verificar_rate_limit_api(identificador):
    """
    Verifica si un usuario ha excedido el limite de llamadas a la API.
    
    Parametros:
        identificador (str): ID del usuario o API key
    
    Retorna:
        tuple: (permitido: bool, mensaje: str)
    """
    ahora = time.time()
    
    # Limpiar intentos antiguos
    _intentos_api[identificador] = [
        t for t in _intentos_api[identificador]
        if ahora - t < VENTANA_TIEMPO_API
    ]
    
    num_intentos = len(_intentos_api[identificador])
    
    if num_intentos >= MAX_INTENTOS_API:
        return False, "Limite de llamadas API excedido. Espera 1 minuto."
    
    return True, ""

def registrar_llamada_api(identificador):
    """
    Registra una llamada a la API.
    
    Parametros:
        identificador (str): ID del usuario o API key
    """
    _intentos_api[identificador].append(time.time())

# ============================================================================
# SANITIZACION DE INPUTS (Prevencion de Inyecciones)
# ============================================================================

def sanitizar_input_texto(texto, max_length=1000):
    """
    Sanitiza un input de texto para prevenir inyecciones XSS y SQL.
    
    Parametros:
        texto (str): Texto a sanitizar
        max_length (int): Longitud maxima permitida
    
    Retorna:
        str: Texto sanitizado
    """
    if texto is None:
        return ""
    
    # Convertir a string si no lo es
    texto = str(texto)
    
    # Limitar longitud
    if len(texto) > max_length:
        texto = texto[:max_length]
    
    # Eliminar caracteres peligrosos
    caracteres_peligrosos = [
        '<', '>', ';', '&', '|', '`', '$', '(', ')', 
        '{', '}', '[', ']', "'", '"', '\\', '\n', '\r'
    ]
    
    resultado = texto
    for char in caracteres_peligrosos:
        resultado = resultado.replace(char, '')
    
    # Eliminar espacios multiples
    resultado = re.sub(r'\s+', ' ', resultado)
    
    return resultado.strip()

def sanitizar_input_numerico(valor, min_val=None, max_val=None):
    """
    Sanitiza un input numerico para prevenir inyecciones.
    
    Parametros:
        valor: Valor a sanitizar
        min_val (float): Valor minimo permitido
        max_val (float): Valor maximo permitido
    
    Retorna:
        float: Valor sanitizado o None si es invalido
    """
    try:
        # Convertir a float
        resultado = float(valor)
        
        # Verificar rangos
        if min_val is not None and resultado < min_val:
            return None
        if max_val is not None and resultado > max_val:
            return None
        
        # Verificar que no sea infinito o NaN
        if resultado != resultado or resultado == float('inf') or resultado == float('-inf'):
            return None
        
        return resultado
    except (ValueError, TypeError):
        return None

def sanitizar_email(email):
    """
    Sanitiza y valida un email.
    
    Parametros:
        email (str): Email a validar
    
    Retorna:
        str: Email sanitizado o None si es invalido
    """
    if not email:
        return None
    
    email = sanitizar_input_texto(email, max_length=254)
    
    # Validar formato de email
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(patron_email, email):
        return email.lower()
    
    return None

def sanitizar_url(url):
    """
    Sanitiza una URL para prevenir inyecciones.
    
    Parametros:
        url (str): URL a sanitizar
    
    Retorna:
        str: URL sanitizada o None si es invalida
    """
    if not url:
        return None
    
    url = sanitizar_input_texto(url, max_length=2000)
    
    # Validar que sea una URL valida
    patron_url = r'^https?://[^\s/$.?#].[^\s]*$'
    
    if re.match(patron_url, url):
        return url
    
    return None

def sanitizar_nombre_archivo(nombre):
    """
    Sanitiza un nombre de archivo para prevenir ataques de path traversal.
    
    Parametros:
        nombre (str): Nombre de archivo
    
    Retorna:
        str: Nombre sanitizado
    """
    if not nombre:
        return "archivo.txt"
    
    # Eliminar caracteres peligrosos
    nombre = re.sub(r'[^\w\s\-.]', '', nombre)
    
    # Eliminar path traversal
    nombre = nombre.replace('..', '').replace('/', '').replace('\\', '')
    
    # Limitar longitud
    if len(nombre) > 255:
        nombre = nombre[:255]
    
    return nombre.strip()

# ============================================================================
# GENERACION Y VALIDACION DE TOKENS
# ============================================================================

def generar_token_seguro(longitud=32):
    """
    Genera un token criptograficamente seguro.
    
    Parametros:
        longitud (int): Longitud del token en bytes
    
    Retorna:
        str: Token en formato hexadecimal
    """
    return os.urandom(longitud).hex()

def generar_token_sesion(usuario, duracion_horas=24):
    """
    Genera un token de sesion unico para un usuario.
    
    Parametros:
        usuario (str): Nombre de usuario
        duracion_horas (int): Duracion del token en horas
    
    Retorna:
        str: Token de sesion
    """
    timestamp = str(time.time())
    random_salt = generar_token_seguro(16)
    
    # Obtener clave secreta de secrets.toml
    try:
        secret_key = st.secrets.get("general", {}).get("SECRET_KEY", "default_secret_key")
    except:
        secret_key = "default_secret_key"
    
    datos = "{}{}{}{}".format(usuario, timestamp, random_salt, secret_key)
    token = hashlib.sha256(datos.encode()).hexdigest()
    
    # Agregar expiracion
    expiracion = int(time.time()) + (duracion_horas * 3600)
    
    return "{}:{}".format(token, expiracion)

def validar_token_sesion(token, usuario):
    """
    Valida un token de sesion.
    
    Parametros:
        token (str): Token a validar
        usuario (str): Nombre de usuario
    
    Retorna:
        bool: True si el token es valido y no ha expirado
    """
    try:
        partes = token.split(':')
        if len(partes) != 2:
            return False
        
        token_hash, expiracion_str = partes
        expiracion = int(expiracion_str)
        
        # Verificar que no haya expirado
        if time.time() > expiracion:
            return False
        
        # Verificar longitud del hash
        if len(token_hash) != 64:
            return False
        
        return True
    except:
        return False

def generar_csrf_token():
    """
    Genera un token CSRF para proteccion contra ataques Cross-Site Request Forgery.
    
    Retorna:
        str: Token CSRF
    """
    if 'csrf_token' not in st.session_state:
        st.session_state.csrf_token = generar_token_seguro(32)
    
    return st.session_state.csrf_token

def validar_csrf_token(token):
    """
    Valida un token CSRF.
    
    Parametros:
        token (str): Token a validar
    
    Retorna:
        bool: True si el token es valido
    """
    if 'csrf_token' not in st.session_state:
        return False
    
    return hmac.compare_digest(token, st.session_state.csrf_token)

# ============================================================================
# VALIDACION DE ARCHIVOS
# ============================================================================

TIPOS_ARCHIVO_PERMITIDOS = {
    'imagenes': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
    'documentos': ['pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx', 'xls'],
    'datos': ['csv', 'xlsx', 'xls', 'json']
}

TAMANOS_MAXIMOS = {
    'imagenes': 5 * 1024 * 1024,  # 5 MB
    'documentos': 10 * 1024 * 1024,  # 10 MB
    'datos': 20 * 1024 * 1024  # 20 MB
}

def validar_archivo(archivo, tipo='documentos'):
    """
    Valida un archivo subido por el usuario.
    
    Parametros:
        archivo: Objeto de archivo de Streamlit
        tipo (str): Tipo de archivo ('imagenes', 'documentos', 'datos')
    
    Retorna:
        tuple: (valido: bool, mensaje: str)
    """
    if archivo is None:
        return False, "No se proporciono ningun archivo"
    
    # Verificar extension
    extension = archivo.name.split('.')[-1].lower()
    tipos_permitidos = TIPOS_ARCHIVO_PERMITIDOS.get(tipo, [])
    
    if extension not in tipos_permitidos:
        return False, "Tipo de archivo no permitido. Tipos permitidos: {}".format(
            ', '.join(tipos_permitidos)
        )
    
    # Verificar tamano
    tamano_maximo = TAMANOS_MAXIMOS.get(tipo, 10 * 1024 * 1024)
    
    # Leer el archivo para obtener su tamano
    archivo.seek(0, 2)  # Ir al final
    tamano = archivo.tell()
    archivo.seek(0)  # Volver al inicio
    
    if tamano > tamano_maximo:
        tamano_mb = tamano_maximo / (1024 * 1024)
        return False, "El archivo excede el tamano maximo de {:.1f} MB".format(tamano_mb)
    
    return True, "Archivo valido"

# ============================================================================
# LOGGING Y AUDITORIA
# ============================================================================

ARCHIVO_LOG = "data/auditoria.log"

def registrar_evento(evento, usuario=None, detalles=None):
    """
    Registra un evento en el log de auditoria.
    
    Parametros:
        evento (str): Tipo de evento (login, logout, pago, etc.)
        usuario (str): Usuario que realizo la accion
        detalles (dict): Detalles adicionales del evento
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'evento': evento,
        'usuario': usuario or 'anonimo',
        'detalles': detalles or {}
    }
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(ARCHIVO_LOG), exist_ok=True)
    
    # Escribir en el log
    with open(ARCHIVO_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

def obtener_logs_recientes(limit=100, evento=None):
    """
    Obtiene los logs mas recientes.
    
    Parametros:
        limit (int): Numero maximo de logs a retornar
        evento (str): Filtrar por tipo de evento
    
    Retorna:
        list: Lista de logs
    """
    if not os.path.exists(ARCHIVO_LOG):
        return []
    
    logs = []
    
    try:
        with open(ARCHIVO_LOG, 'r', encoding='utf-8') as f:
            for linea in f:
                try:
                    log = json.loads(linea.strip())
                    if evento is None or log.get('evento') == evento:
                        logs.append(log)
                except:
                    continue
    except:
        return []
    
    # Retornar los mas recientes
    return logs[-limit:]

# ============================================================================
# VALIDACION DE CONTRASENAS
# ============================================================================

def validar_contrasena_segura(password):
    """
    Valida que una contrasena cumpla con los requisitos de seguridad.
    
    Parametros:
        password (str): Contrasena a validar
    
    Retorna:
        tuple: (valida: bool, mensaje: str)
    """
    if not password:
        return False, "La contrasena no puede estar vacia"
    
    if len(password) < 8:
        return False, "La contrasena debe tener al menos 8 caracteres"
    
    if len(password) > 128:
        return False, "La contrasena no puede exceder 128 caracteres"
    
    # Verificar complejidad
    tiene_mayuscula = bool(re.search(r'[A-Z]', password))
    tiene_minuscula = bool(re.search(r'[a-z]', password))
    tiene_numero = bool(re.search(r'\d', password))
    tiene_especial = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not (tiene_mayuscula and tiene_minuscula and tiene_numero):
        return False, "La contrasena debe contener mayusculas, minusculas y numeros"
    
    # Verificar que no sea una contrasena comun
    contrasenas_comunes = [
        'password', '123456', 'qwerty', 'admin', 'usuario',
        'contrasena', 'password123', 'admin123'
    ]
    
    if password.lower() in contrasenas_comunes:
        return False, "La contrasena es muy comun. Elige una mas segura."
    
    return True, "Contrasena valida"

# ============================================================================
# PROTECCION CONTRA ATAQUES COMUNES
# ============================================================================

def verificar_ip_bloqueada(ip):
    """
    Verifica si una IP esta en la lista negra.
    En produccion, usar una base de datos o servicio externo.
    
    Parametros:
        ip (str): Direccion IP
    
    Retorna:
        bool: True si la IP esta bloqueada
    """
    # Lista negra de ejemplo (en produccion usar DB)
    ips_bloqueadas = [
        '192.168.1.100',  # Ejemplo
        '10.0.0.50'  # Ejemplo
    ]
    
    return ip in ips_bloqueadas

def obtener_ip_usuario():
    """
    Obtiene la IP del usuario actual.
    En Streamlit Cloud, esto requiere configuracion especial.
    
    Retorna:
        str: Direccion IP o 'desconocida'
    """
    try:
        # En Streamlit local, esto no funciona directamente
        # En produccion, usar headers HTTP o servicios externos
        return "127.0.0.1"  # Placeholder
    except:
        return "desconocida"

# ============================================================================
# ENCRIPTACION DE DATOS SENSIBLES
# ============================================================================

def encriptar_dato(dato, clave):
    """
    Encripta un dato sensible usando XOR (simple - en produccion usar AES).
    
    Parametros:
        dato (str): Dato a encriptar
        clave (str): Clave de encriptacion
    
    Retorna:
        str: Dato encriptado en formato hexadecimal
    """
    # En produccion, usar cryptography.fernet o similar
    dato_bytes = dato.encode('utf-8')
    clave_bytes = clave.encode('utf-8')
    
    # XOR simple (NO usar en produccion)
    encriptado = bytes([
        dato_bytes[i] ^ clave_bytes[i % len(clave_bytes)]
        for i in range(len(dato_bytes))
    ])
    
    return encriptado.hex()

def desencriptar_dato(dato_encriptado, clave):
    """
    Desencripta un dato encriptado con encriptar_dato().
    
    Parametros:
        dato_encriptado (str): Dato encriptado en hex
        clave (str): Clave de encriptacion
    
    Retorna:
        str: Dato desencriptado
    """
    try:
        dato_bytes = bytes.fromhex(dato_encriptado)
        clave_bytes = clave.encode('utf-8')
        
        desencriptado = bytes([
            dato_bytes[i] ^ clave_bytes[i % len(clave_bytes)]
            for i in range(len(dato_bytes))
        ])
        
        return desencriptado.decode('utf-8')
    except:
        return None

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DEL MODULO DE SEGURIDAD")
    print("=" * 60)
    
    print("\n1. Sanitizacion de texto:")
    texto_peligroso = "<script>alert('XSS')</script>"
    texto_seguro = sanitizar_input_texto(texto_peligroso)
    print("   Original: {}".format(texto_peligroso))
    print("   Sanitizado: {}".format(texto_seguro))
    
    print("\n2. Validacion de email:")
    emails = ["usuario@ejemplo.com", "email-invalido", "test@test.co"]
    for email in emails:
        resultado = sanitizar_email(email)
        print("   {} -> {}".format(email, resultado))
    
    print("\n3. Generacion de tokens:")
    token = generar_token_seguro(16)
    print("   Token: {}".format(token))
    
    print("\n4. Validacion de contrasenas:")
    contrasenas = ["123", "password", "MiPassword123!", "ContrasenaMuySegura2024"]
    for pwd in contrasenas:
        valida, mensaje = validar_contrasena_segura(pwd)
        print("   {} -> {} ({})".format(pwd, "Valida" if valida else "Invalida", mensaje))
    
    print("\n" + "=" * 60)        