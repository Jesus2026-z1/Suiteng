"""
Rutas de administrador.
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Usuario
from security import requerir_auth, requerir_admin, registrar_log

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@requerir_auth
@requerir_admin
def get_all_users():
    """Lista todos los usuarios (solo admin)."""
    usuarios = Usuario.query.all()
    return jsonify({
        'success': True,
        'users': [u.to_dict() for u in usuarios]
    }), 200


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@requerir_auth
@requerir_admin
def toggle_user_active(user_id):
    """Activa/desactiva un usuario."""
    usuario = Usuario.query.get_or_404(user_id)
    usuario.activo = not usuario.activo
    db.session.commit()
    
    registrar_log('toggle_user', request.current_user.username, 
                  f"Usuario {usuario.username} {'activado' if usuario.activo else 'desactivado'}")
    
    return jsonify({'success': True, 'activo': usuario.activo}), 200