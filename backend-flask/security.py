"""
Funciones de seguridad y utilidades.
"""
import secrets
import re
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from extensions import db
from models import Usuario, TokenBloqueado, LogAuditoria
from config import Config


def generar_token_jwt(usuario_id, username, rol):
    """Genera un token JWT seguro."""
    payload = {
        'user_id': usuario_id,
        'username': username,
        'rol': rol,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'jti': secrets.token_hex(16)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')


def verificar_token_jwt(token):
    """Verifica y decodifica un token JWT."""
    try:
        # Verificar si el token está en la lista negra
        token_bloqueado = TokenBloqueado.query.filter_by(token=token).first()
        if token_bloqueado:
            return None, 'Token revocado'
        
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expirado'
    except jwt.InvalidTokenError:
        return None, 'Token inválido'


def requerir_auth(f):
    """Decorator para proteger rutas."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        # Remover 'Bearer ' del token
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload, error = verificar_token_jwt(token)
        if error:
            return jsonify({'error': error}), 401
        
        # Obtener usuario de la base de datos
        usuario = Usuario.query.get(payload['user_id'])
        if not usuario or not usuario.activo:
            return jsonify({'error': 'Usuario no encontrado o desactivado'}), 401
        
        # Verificar email verificado (excepto para rutas de verificación)
        if not usuario.email_verificado and request.endpoint not in ['auth.verificar_email', 'auth.reenviar_verificacion']:
            return jsonify({'error': 'Email no verificado. Por favor verifica tu email.'}), 403
        
        # Agregar usuario al request
        request.current_user = usuario
        return f(*args, **kwargs)
    
    return decorated


def requerir_admin(f):
    """Decorator para rutas de administrador."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user.rol != 'admin':
            return jsonify({'error': 'No autorizado'}), 403
        return f(*args, **kwargs)
    return decorated


def registrar_log(evento, usuario=None, detalles=None):
    """Registra un evento en el log de auditoría."""
    log = LogAuditoria(
        usuario=usuario,
        evento=evento,
        ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        detalles=detalles
    )
    db.session.add(log)
    db.session.commit()


def sanitizar_input(texto, max_length=100):
    """Sanitiza inputs para prevenir XSS e inyecciones."""
    if not texto:
        return ''
    texto = str(texto)[:max_length]
    # Eliminar caracteres peligrosos
    texto = re.sub(r'[<>"\';&|`$]', '', texto)
    return texto.strip()


def validar_email(email):
    """Valida formato de email."""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_contrasena_segura(password):
    """Valida que la contraseña sea segura."""
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    if len(password) > 128:
        return False, "Máximo 128 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "Debe contener al menos un número"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Debe contener al menos un carácter especial"
    return True, "Contraseña válida"


def crear_admin_inicial():
    """Crea un usuario admin si no existe."""
    from config import Config
    
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email=Config.ADMIN_EMAIL,
            nombre_completo='Administrador',
            rol='admin',
            email_verificado=True
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print("✓ Usuario admin creado")