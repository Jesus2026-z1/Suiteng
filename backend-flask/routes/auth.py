"""
Rutas de autenticación: login, registro, recuperación de contraseña.
"""
from flask import Blueprint, request, jsonify
from extensions import db, mail, limiter
from models import Usuario
from security import (
    generar_token_jwt, sanitizar_input, validar_email,
    validar_contrasena_segura, registrar_log
)
from config import Config
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Registro de nuevo usuario con verificación de email."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos no proporcionados'}), 400
    
    username = sanitizar_input(data.get('username', ''), 50)
    email = sanitizar_input(data.get('email', ''), 120).lower()
    password = data.get('password', '')
    nombre_completo = sanitizar_input(data.get('nombre_completo', ''), 100)
    
    # Validaciones
    if not username or not email or not password or not nombre_completo:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    
    if not validar_email(email):
        return jsonify({'error': 'Email inválido'}), 400
    
    valida, mensaje = validar_contrasena_segura(password)
    if not valida:
        return jsonify({'error': mensaje}), 400
    
    # Verificar si ya existe
    if Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first():
        return jsonify({'error': 'Usuario o email ya registrado'}), 409
    
    # Crear usuario
    usuario = Usuario(
        username=username,
        email=email,
        nombre_completo=nombre_completo,
        token_verificacion=secrets.token_urlsafe(32)
    )
    usuario.set_password(password)
    
    db.session.add(usuario)
    db.session.commit()
    
    # Enviar email de verificación
    try:
        url_verificacion = f"{Config.FRONTEND_URL}/verificar-email?token={usuario.token_verificacion}"
        msg = Message(
            'Verifica tu email - Sistema de Análisis',
            sender=Config.MAIL_USERNAME,
            recipients=[email]
        )
        msg.body = f"""
        Hola {nombre_completo},
        
        Gracias por registrarte. Por favor verifica tu email haciendo clic en el siguiente enlace:
        
        {url_verificacion}
        
        Este enlace expira en 24 horas.
        
        Si no te registraste, ignora este email.
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error enviando email: {e}")
    
    registrar_log('registro_usuario', username, f"Email: {email}")
    
    return jsonify({
        'success': True,
        'message': 'Usuario registrado. Por favor verifica tu email.'
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """Login con verificación de seguridad."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos no proporcionados'}), 400
    
    username = sanitizar_input(data.get('username', ''), 50)
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    # Buscar usuario
    usuario = Usuario.query.filter_by(username=username).first()
    
    if not usuario:
        # Comparación en tiempo constante para prevenir timing attacks
        check_password_hash('hash_falso', password)
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Verificar si está bloqueado
    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
        minutos_restantes = int((usuario.bloqueado_hasta - datetime.utcnow()).total_seconds() / 60)
        return jsonify({
            'error': f'Cuenta bloqueada. Intenta en {minutos_restantes} minutos'
        }), 429
    
    # Verificar contraseña
    if not usuario.check_password(password):
        usuario.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos
        if usuario.intentos_fallidos >= 5:
            usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=30)
            usuario.intentos_fallidos = 0
            db.session.commit()
            registrar_log('cuenta_bloqueada', username)
            return jsonify({'error': 'Cuenta bloqueada por 30 minutos'}), 429
        
        db.session.commit()
        return jsonify({
            'error': 'Credenciales inválidas',
            'intentos_restantes': 5 - usuario.intentos_fallidos
        }), 401
    
    # Login exitoso
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.ultimo_login = datetime.utcnow()
    db.session.commit()
    
    # Generar token JWT
    token = generar_token_jwt(usuario.id, usuario.username, usuario.rol)
    
    registrar_log('login_exitoso', username, f"IP: {request.remote_addr}")
    
    return jsonify({
        'success': True,
        'token': token,
        'user': usuario.to_dict()
    }), 200


@auth_bp.route('/verificar-email', methods=['GET'])
def verificar_email():
    """Verifica el email del usuario."""
    token = request.args.get('token')
    
    if not token:
        return jsonify({'error': 'Token no proporcionado'}), 400
    
    usuario = Usuario.query.filter_by(token_verificacion=token).first()
    
    if not usuario:
        return jsonify({'error': 'Token inválido'}), 400
    
    # Verificar que no haya expirado (24 horas)
    if (datetime.utcnow() - usuario.fecha_registro).total_seconds() > 86400:
        return jsonify({'error': 'Token expirado'}), 400
    
    usuario.email_verificado = True
    usuario.token_verificacion = None
    db.session.commit()
    
    registrar_log('email_verificado', usuario.username)
    
    return jsonify({'success': True, 'message': 'Email verificado exitosamente'}), 200


@auth_bp.route('/recuperar-contrasena', methods=['POST'])
@limiter.limit("3 per hour")
def recuperar_contrasena():
    """Envía email para recuperar contraseña."""
    data = request.get_json()
    email = sanitizar_input(data.get('email', ''), 120).lower()
    
    if not email:
        return jsonify({'error': 'Email requerido'}), 400
    
    usuario = Usuario.query.filter_by(email=email).first()
    
    # Siempre retornar éxito para no revelar si el email existe
    if usuario:
        token_reset = secrets.token_urlsafe(32)
        usuario.token_reset = token_reset
        usuario.token_reset_expira = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # Enviar email
        try:
            url_reset = f"{Config.FRONTEND_URL}/reset-password?token={token_reset}"
            msg = Message(
                'Recuperación de contraseña',
                sender=Config.MAIL_USERNAME,
                recipients=[email]
            )
            msg.body = f"""
            Hola {usuario.nombre_completo},
            
            Recibimos una solicitud para recuperar tu contraseña.
            
            Haz clic en el siguiente enlace para crear una nueva contraseña:
            {url_reset}
            
            Este enlace expira en 1 hora.
            
            Si no solicitaste esto, ignora este email.
            """
            mail.send(msg)
        except Exception as e:
            print(f"Error enviando email: {e}")
    
    return jsonify({'success': True, 'message': 'Si el email existe, recibirás un enlace de recuperación'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Resetea la contraseña con el token."""
    data = request.get_json()
    token = data.get('token')
    nueva_password = data.get('password')
    
    if not token or not nueva_password:
        return jsonify({'error': 'Token y nueva contraseña requeridos'}), 400
    
    valida, mensaje = validar_contrasena_segura(nueva_password)
    if not valida:
        return jsonify({'error': mensaje}), 400
    
    usuario = Usuario.query.filter_by(token_reset=token).first()
    
    if not usuario or not usuario.token_reset_expira or usuario.token_reset_expira < datetime.utcnow():
        return jsonify({'error': 'Token inválido o expirado'}), 400
    
    usuario.set_password(nueva_password)
    usuario.token_reset = None
    usuario.token_reset_expira = None
    db.session.commit()
    
    registrar_log('password_reset', usuario.username)
    
    return jsonify({'success': True, 'message': 'Contraseña actualizada'}), 200