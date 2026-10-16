"""
Rutas para el módulo de comentarios.
Maneja CRUD de comentarios con seguridad.
"""
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Comment
from services.comment_service import CommentService
from security import requerir_auth, requerir_admin, registrar_log, sanitizar_input
from datetime import datetime

comments_bp = Blueprint('comments', __name__)

# ============================================================
# RUTAS PÚBLICAS
# ============================================================

@comments_bp.route('/api/comments', methods=['GET'])
def get_comments():
    """
    Obtiene comentarios aprobados.
    Soporta paginación.
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Limitar valores
        limit = min(max(limit, 1), 50)
        offset = max(offset, 0)
        
        comments = CommentService.get_approved_comments(limit, offset)
        stats = CommentService.get_comment_stats()
        
        return jsonify({
            'success': True,
            'comments': comments,
            'stats': stats,
            'total': stats['total']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comments_bp.route('/api/comments', methods=['POST'])
@limiter.limit("5 per hour")
def create_comment():
    """
    Crea un nuevo comentario.
    Requiere aprobación antes de ser público.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos no proporcionados'}), 400
        
        # Crear comentario
        result = CommentService.create_comment(
            data,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if result['success']:
            registrar_log('comment_created', data.get('name', 'Anónimo'), {
                'rating': data.get('rating'),
                'comment_id': result['comment'].id
            })
            
            return jsonify({
                'success': True,
                'message': 'Comentario enviado. Será publicado después de revisión.',
                'comment_id': result['comment'].id
            }), 201
        else:
            return jsonify({
                'success': False,
                'errors': result['errors']
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comments_bp.route('/api/comments/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas de comentarios."""
    try:
        stats = CommentService.get_comment_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# RUTAS DE ADMINISTRADOR
# ============================================================

@comments_bp.route('/api/comments/pending', methods=['GET'])
@requerir_auth
@requerir_admin
def get_pending_comments():
    """Obtiene comentarios pendientes de aprobación."""
    try:
        comments = Comment.query.filter_by(status='pending')\
            .order_by(Comment.created_at.desc())\
            .all()
        
        return jsonify({
            'success': True,
            'comments': [c.to_dict(include_email=True) for c in comments]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comments_bp.route('/api/comments/<int:comment_id>/approve', methods=['POST'])
@requerir_auth
@requerir_admin
def approve_comment(comment_id):
    """Aprueba un comentario."""
    try:
        comment = CommentService.approve_comment(comment_id)
        
        registrar_log('comment_approved', request.current_user.username, {
            'comment_id': comment_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Comentario aprobado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comments_bp.route('/api/comments/<int:comment_id>/reject', methods=['POST'])
@requerir_auth
@requerir_admin
def reject_comment(comment_id):
    """Rechaza un comentario."""
    try:
        comment = CommentService.reject_comment(comment_id)
        
        registrar_log('comment_rejected', request.current_user.username, {
            'comment_id': comment_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Comentario rechazado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@comments_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@requerir_auth
@requerir_admin
def delete_comment(comment_id):
    """Elimina un comentario."""
    try:
        CommentService.delete_comment(comment_id)
        
        registrar_log('comment_deleted', request.current_user.username, {
            'comment_id': comment_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Comentario eliminado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500