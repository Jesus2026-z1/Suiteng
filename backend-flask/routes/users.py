"""
Rutas de usuario: perfil, logout.
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import TokenBloqueado
from security import requerir_auth, verificar_token_jwt, registrar_log
from datetime import datetime

users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@requerir_auth
def get_current_user():
    """Obtiene información del usuario actual."""
    return jsonify({
        'success': True,
        'user': request.current_user.to_dict()
    }), 200


@users_bp.route('/logout', methods=['POST'])
@requerir_auth
def logout():
    """Cierra sesión y revoca el token."""
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]
    
    # Agregar token a lista negra
    payload, _ = verificar_token_jwt(token)
    if payload:
        token_bloqueado = TokenBloqueado(
            token=token,
            fecha_expiracion=datetime.fromtimestamp(payload['exp'])
        )
        db.session.add(token_bloqueado)
        db.session.commit()
    
    registrar_log('logout', request.current_user.username)
    
    return jsonify({'success': True, 'message': 'Sesión cerrada'}), 200