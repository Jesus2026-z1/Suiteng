"""
Rutas de OAuth: Google y GitHub.
"""
from flask import Blueprint, request, jsonify
from extensions import db, oauth
from models import Usuario
from security import generar_token_jwt, registrar_log

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/google')
def google_login():
    """Inicia login con Google."""
    redirect_uri = request.url_root + 'api/auth/google/callback'
    return oauth.google.authorize_redirect(redirect_uri)


@oauth_bp.route('/google/callback')
def google_callback():
    """Callback de Google OAuth."""
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        
        if not userinfo:
            return jsonify({'error': 'No se pudo obtener información del usuario'}), 400
        
        email = userinfo['email']
        nombre = userinfo.get('name', email)
        google_id = userinfo['sub']
        
        # Buscar o crear usuario
        usuario = Usuario.query.filter_by(google_id=google_id).first()
        
        if not usuario:
            # Verificar si el email ya está registrado
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario:
                # Asociar cuenta existente con Google
                usuario.google_id = google_id
                usuario.email_verificado = True
            else:
                # Crear nuevo usuario
                username = email.split('@')[0]
                # Asegurar que el username sea único
                base_username = username
                contador = 1
                while Usuario.query.filter_by(username=username).first():
                    username = f"{base_username}{contador}"
                    contador += 1
                
                usuario = Usuario(
                    username=username,
                    email=email,
                    nombre_completo=nombre,
                    google_id=google_id,
                    email_verificado=True
                )
                # Contraseña aleatoria (no se usará)
                usuario.set_password('token_inseguro_' + __import__('secrets').token_urlsafe(32))
                db.session.add(usuario)
        
        db.session.commit()
        
        # Generar token
        token = generar_token_jwt(usuario.id, usuario.username, usuario.rol)
        
        registrar_log('oauth_google', usuario.username)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': usuario.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error en Google OAuth: {e}")
        return jsonify({'error': 'Error en autenticación con Google'}), 500


@oauth_bp.route('/github')
def github_login():
    """Inicia login con GitHub."""
    redirect_uri = request.url_root + 'api/auth/github/callback'
    return oauth.github.authorize_redirect(redirect_uri)


@oauth_bp.route('/github/callback')
def github_callback():
    """Callback de GitHub OAuth."""
    try:
        token = oauth.github.authorize_access_token()
        
        # Obtener información del usuario
        resp = oauth.github.get('user')
        userinfo = resp.json()
        
        # Obtener email
        email_resp = oauth.github.get('user/emails')
        emails = email_resp.json()
        email = next((e['email'] for e in emails if e['primary']), None)
        
        if not email:
            return jsonify({'error': 'No se pudo obtener el email'}), 400
        
        github_id = str(userinfo['id'])
        nombre = userinfo.get('name', userinfo.get('login', email))
        
        # Buscar o crear usuario
        usuario = Usuario.query.filter_by(github_id=github_id).first()
        
        if not usuario:
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario:
                usuario.github_id = github_id
                usuario.email_verificado = True
            else:
                username = userinfo.get('login', email.split('@')[0])
                base_username = username
                contador = 1
                while Usuario.query.filter_by(username=username).first():
                    username = f"{base_username}{contador}"
                    contador += 1
                
                usuario = Usuario(
                    username=username,
                    email=email,
                    nombre_completo=nombre,
                    github_id=github_id,
                    email_verificado=True
                )
                usuario.set_password('token_inseguro_' + __import__('secrets').token_urlsafe(32))
                db.session.add(usuario)
        
        db.session.commit()
        
        token = generar_token_jwt(usuario.id, usuario.username, usuario.rol)
        
        registrar_log('oauth_github', usuario.username)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': usuario.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error en GitHub OAuth: {e}")
        return jsonify({'error': 'Error en autenticación con GitHub'}), 500