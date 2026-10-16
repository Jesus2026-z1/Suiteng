"""
Modulo de Autenticacion para la aplicacion Streamlit.
Gestiona login, sesiones, roles y control de acceso.
"""

import streamlit as st
import hashlib
import hmac
import time

# ============================================================================
# BASE DE DATOS DE USUARIOS (en produccion usar base de datos real)
# ============================================================================

# Para generar hashes de contraseñas, usa la funcion generar_hash_password()
# que esta al final de este archivo.

USUARIOS_AUTORIZADOS = {
    "admin": {
        # Contrasena: "admin123"
        "password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
        "rol": "admin",
        "nombre_completo": "Administrador del Sistema",
        "email": "admin@tuempresa.com",
        "paginas_permitidas": ["Minimos_Cuadrados", "Optimizacion", "Pagos", "Donativos"],
        "activo": True
    },
    "usuario1": {
        # Contrasena: "usuario123"
        "password_hash": "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5",
        "rol": "usuario",
        "nombre_completo": "Usuario de Prueba",
        "email": "usuario1@tuempresa.com",
        "paginas_permitidas": ["Minimos_Cuadrados", "Donativos"],
        "activo": True
    },
    "demo": {
        # Contrasena: "demo123"
        "password_hash": "6b3a55e0261b0304143f805a24924d0c1d44bb25f7fb88bea5415ee94eaf6bd9",
        "rol": "demo",
        "nombre_completo": "Usuario Demostracion",
        "email": "demo@tuempresa.com",
        "paginas_permitidas": ["Minimos_Cuadrados"],
        "activo": True
    }
}

# ============================================================================
# FUNCIONES DE HASH Y VERIFICACION
# ============================================================================

def hash_password(password):
    """
    Genera el hash SHA-256 de una contrasena.
    
    Parametros:
        password (str): La contrasena en texto plano
    
    Retorna:
        str: El hash SHA-256 en formato hexadecimal
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verificar_password(password, hash_almacenado):
    """
    Verifica si una contrasena coincide con su hash usando comparacion segura.
    Usa hmac.compare_digest para prevenir ataques de temporizacion.
    
    Parametros:
        password (str): Contrasena en texto plano
        hash_almacenado (str): Hash almacenado en la base de datos
    
    Retorna:
        bool: True si coincide, False si no
    """
    password_hash = hash_password(password)
    return hmac.compare_digest(password_hash, hash_almacenado)

def generar_hash_password():
    """
    Funcion auxiliar para generar hashes de nuevas contrasenas.
    Usala desde la terminal para agregar nuevos usuarios.
    
    Ejemplo de uso:
        >>> generar_hash_password("mi_contrasena_segura")
        'abc123def456...'
    """
    import getpass
    password = getpass.getpass("Ingresa la contrasena: ")
    hash_resultado = hash_password(password)
    print("\nHash generado:")
    print(hash_resultado)
    print("\nAgrega esto a tu diccionario USUARIOS_AUTORIZADOS:")
    print('"password_hash": "{}",'.format(hash_resultado))
    return hash_resultado

# ============================================================================
# FUNCIONES DE LOGIN Y SESION
# ============================================================================

def inicializar_sesion():
    """
    Inicializa las variables de sesion si no existen.
    Debe llamarse al inicio de cada pagina protegida.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "rol" not in st.session_state:
        st.session_state.rol = None
    if "nombre_completo" not in st.session_state:
        st.session_state.nombre_completo = None
    if "email" not in st.session_state:
        st.session_state.email = None
    if "paginas_permitidas" not in st.session_state:
        st.session_state.paginas_permitidas = []
    if "login_time" not in st.session_state:
        st.session_state.login_time = None
    if "intentos_fallidos" not in st.session_state:
        st.session_state.intentos_fallidos = 0
    if "bloqueo_hasta" not in st.session_state:
        st.session_state.bloqueo_hasta = None

def login():
    """
    Muestra el formulario de login y gestiona la autenticacion.
    
    Retorna:
        bool: True si el usuario esta autenticado, False si no
    """
    inicializar_sesion()
    
    # Si ya esta logueado, retornar True
    if st.session_state.logged_in:
        # Verificar que la sesion no haya expirado
        if verificar_sesion_activa():
            return True
        else:
            logout()
            return False
    
    # Verificar si hay bloqueo por intentos fallidos
    if st.session_state.bloqueo_hasta:
        tiempo_restante = st.session_state.bloqueo_hasta - time.time()
        if tiempo_restante > 0:
            minutos = int(tiempo_restante / 60) + 1
            st.error("Cuenta bloqueada temporalmente. Intenta de nuevo en {} minuto(s).".format(minutos))
            return False
        else:
            # Desbloquear
            st.session_state.bloqueo_hasta = None
            st.session_state.intentos_fallidos = 0
    
    # Mostrar formulario de login
    st.markdown("---")
    st.subheader("Inicio de Sesion")
    st.write("Ingresa tus credenciales para acceder al sistema")
    
    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="Ej: admin, usuario1, demo")
        password = st.text_input("Contrasena", type="password", placeholder="Ingresa tu contrasena")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit = st.form_submit_button("Iniciar Sesion", use_container_width=True)
    
    if submit:
        # Validar campos vacios
        if not username or not password:
            st.error("Por favor completa todos los campos")
            return False
        
        # Verificar si el usuario existe
        if username in USUARIOS_AUTORIZADOS:
            usuario_data = USUARIOS_AUTORIZADOS[username]
            
            # Verificar si la cuenta esta activa
            if not usuario_data.get("activo", True):
                st.error("Tu cuenta esta desactivada. Contacta al administrador.")
                return False
            
            # Verificar contrasena
            if verificar_password(password, usuario_data["password_hash"]):
                # Login exitoso
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.rol = usuario_data["rol"]
                st.session_state.nombre_completo = usuario_data.get("nombre_completo", username)
                st.session_state.email = usuario_data.get("email", "")
                st.session_state.paginas_permitidas = usuario_data["paginas_permitidas"]
                st.session_state.login_time = time.time()
                st.session_state.intentos_fallidos = 0
                
                st.success("Bienvenido, {}".format(usuario_data.get("nombre_completo", username)))
                st.rerun()
                return True
            else:
                # Contrasena incorrecta
                registrar_intento_fallido()
                st.error("Contrasena incorrecta. Intentos restantes: {}".format(
                    max(0, 5 - st.session_state.intentos_fallidos)
                ))
                return False
        else:
            # Usuario no existe - hacer comparacion en tiempo constante
            # para prevenir ataques de temporizacion
            verificar_password(password, "hash_falso_para_comparacion_segura_123456789")
            registrar_intento_fallido()
            st.error("Usuario no encontrado. Intentos restantes: {}".format(
                max(0, 5 - st.session_state.intentos_fallidos)
            ))
            return False
    
    # Mostrar usuarios de prueba (solo en desarrollo)
    with st.expander("Usuarios de prueba (solo desarrollo)"):
        st.markdown("""
        **Usuarios disponibles para pruebas:**
        
        | Usuario | Contrasena | Rol |
        |---------|------------|-----|
        | admin | admin123 | Administrador |
        | usuario1 | usuario123 | Usuario |
        | demo | demo123 | Demo |
        """)
    
    return False

def logout():
    """
    Cierra la sesion del usuario y limpia todas las variables de sesion.
    """
    keys_a_eliminar = [
        "logged_in", "user", "rol", "nombre_completo", "email",
        "paginas_permitidas", "login_time", "intentos_fallidos", "bloqueo_hasta"
    ]
    
    for key in keys_a_eliminar:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()

def verificar_sesion_activa(timeout_minutos=60):
    """
    Verifica si la sesion del usuario sigue activa (no ha expirado).
    
    Parametros:
        timeout_minutos (int): Minutos de inactividad permitidos
    
    Retorna:
        bool: True si la sesion esta activa, False si expiro
    """
    if not st.session_state.get("logged_in"):
        return False
    
    if st.session_state.get("login_time"):
        tiempo_transcurrido = time.time() - st.session_state.login_time
        if tiempo_transcurrido > timeout_minutos * 60:
            st.warning("Tu sesion ha expirado por inactividad. Por favor inicia sesion nuevamente.")
            return False
    
    return True

def registrar_intento_fallido():
    """
    Registra un intento de login fallido y bloquea la cuenta si se excede el limite.
    """
    st.session_state.intentos_fallidos += 1
    
    # Bloquear despues de 5 intentos fallidos por 5 minutos
    if st.session_state.intentos_fallidos >= 5:
        st.session_state.bloqueo_hasta = time.time() + 300  # 5 minutos
        st.session_state.intentos_fallidos = 0

# ============================================================================
# FUNCIONES DE CONTROL DE ACCESO
# ============================================================================

def verificar_acceso_pagina(nombre_pagina):
    """
    Verifica si el usuario actual tiene acceso a la pagina especificada.
    
    Parametros:
        nombre_pagina (str): Nombre de la pagina a verificar
    
    Retorna:
        bool: True si tiene acceso, False si no
    """
    # Admin tiene acceso total
    if st.session_state.get("rol") == "admin":
        return True
    
    # Verificar paginas permitidas
    paginas_permitidas = st.session_state.get("paginas_permitidas", [])
    return nombre_pagina in paginas_permitidas

def verificar_rol(roles_permitidos):
    """
    Verifica si el usuario tiene uno de los roles permitidos.
    
    Parametros:
        roles_permitidos (list): Lista de roles permitidos
    
    Retorna:
        bool: True si el usuario tiene uno de los roles, False si no
    """
    rol_actual = st.session_state.get("rol")
    return rol_actual in roles_permitidos

def obtener_usuario_actual():
    """
    Retorna la informacion completa del usuario actual.
    
    Retorna:
        dict: Informacion del usuario o None si no hay sesion activa
    """
    if not st.session_state.get("logged_in"):
        return None
    
    username = st.session_state.get("user")
    if username and username in USUARIOS_AUTORIZADOS:
        return USUARIOS_AUTORIZADOS[username]
    
    return None

# ============================================================================
# FUNCIONES DE ADMINISTRACION DE USUARIOS
# ============================================================================

def agregar_usuario(username, password, rol, nombre_completo, email, paginas_permitidas):
    """
    Agrega un nuevo usuario al sistema (solo en memoria, no persistente).
    Para persistencia real, usar base de datos.
    
    Parametros:
        username (str): Nombre de usuario
        password (str): Contrasena en texto plano
        rol (str): Rol del usuario (admin, usuario, demo)
        nombre_completo (str): Nombre completo
        email (str): Email del usuario
        paginas_permitidas (list): Lista de paginas a las que tiene acceso
    
    Retorna:
        bool: True si se agrego exitosamente
    """
    if username in USUARIOS_AUTORIZADOS:
        return False
    
    USUARIOS_AUTORIZADOS[username] = {
        "password_hash": hash_password(password),
        "rol": rol,
        "nombre_completo": nombre_completo,
        "email": email,
        "paginas_permitidas": paginas_permitidas,
        "activo": True
    }
    
    return True

def desactivar_usuario(username):
    """
    Desactiva un usuario sin eliminarlo del sistema.
    
    Parametros:
        username (str): Nombre de usuario a desactivar
    
    Retorna:
        bool: True si se desactivo exitosamente
    """
    if username in USUARIOS_AUTORIZADOS:
        USUARIOS_AUTORIZADOS[username]["activo"] = False
        return True
    return False

def cambiar_contrasena(username, nueva_password):
    """
    Cambia la contrasena de un usuario.
    
    Parametros:
        username (str): Nombre de usuario
        nueva_password (str): Nueva contrasena en texto plano
    
    Retorna:
        bool: True si se cambio exitosamente
    """
    if username in USUARIOS_AUTORIZADOS:
        USUARIOS_AUTORIZADOS[username]["password_hash"] = hash_password(nueva_password)
        return True
    return False

# ============================================================================
# BARRA LATERAL DE USUARIO (COMPONENTE REUTILIZABLE)
# ============================================================================

def mostrar_info_usuario_sidebar():
    """
    Muestra informacion del usuario en la barra lateral.
    Incluye boton de cerrar sesion.
    """
    if not st.session_state.get("logged_in"):
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Usuario Actual")
    
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        # Icono basado en rol
        iconos_rol = {
            "admin": "👑",
            "usuario": "👤",
            "demo": "🎭"
        }
        st.markdown(iconos_rol.get(st.session_state.rol, "👤"))
    
    with col2:
        st.markdown("**{}**".format(st.session_state.nombre_completo))
        st.caption("Rol: {}".format(st.session_state.rol))
    
    if st.sidebar.button("Cerrar Sesion", use_container_width=True):
        logout()

# ============================================================================
# EJEMPLO DE USO (para probar el modulo)
# ============================================================================

if __name__ == "__main__":
    # Este codigo solo se ejecuta si corres el archivo directamente
    # Sirve para probar las funciones
    
    print("=" * 60)
    print("PRUEBA DEL MODULO DE AUTENTICACION")
    print("=" * 60)
    
    print("\n1. Generando hash de una contrasena de prueba:")
    password_prueba = "mi_contrasena_segura"
    hash_generado = hash_password(password_prueba)
    print("   Contrasena: {}".format(password_prueba))
    print("   Hash: {}".format(hash_generado))
    
    print("\n2. Verificando contrasenas:")
    print("   Contrasena correcta: {}".format(verificar_password("admin123", USUARIOS_AUTORIZADOS["admin"]["password_hash"])))
    print("   Contrasena incorrecta: {}".format(verificar_password("incorrecta", USUARIOS_AUTORIZADOS["admin"]["password_hash"])))
    
    print("\n3. Usuarios disponibles:")
    for username, data in USUARIOS_AUTORIZADOS.items():
        print("   - {} ({}): {}".format(username, data["rol"], data["nombre_completo"]))
    
    print("\n" + "=" * 60)
    print("Para generar hashes de nuevas contrasenas, ejecuta:")
    print("  python -c 'from utils.auth import generar_hash_password; generar_hash_password()'")
    print("=" * 60)