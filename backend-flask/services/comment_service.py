"""
Servicio de comentarios con validación y seguridad.
"""
from extensions import db
from models import Comment
from security import sanitizar_input, validar_email
import re
from datetime import datetime

class CommentService:
    """Servicio para gestión de comentarios."""
    
    @staticmethod
    def validate_comment_data(data):
        """
        Valida los datos del comentario.
        
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Validar rating
        rating = data.get('rating')
        if rating is None or rating not in [1, 2, 3, 4, 5]:
            errors.append('Rating debe ser entre 1 y 5')
        
        # Validar contenido
        content = data.get('content', '').strip()
        if not content:
            errors.append('El contenido no puede estar vacío')
        elif len(content) < 10:
            errors.append('El contenido debe tener al menos 10 caracteres')
        elif len(content) > 2000:
            errors.append('El contenido no puede exceder 2000 caracteres')
        
        # Validar título (opcional)
        title = data.get('title', '').strip()
        if title and len(title) > 200:
            errors.append('El título no puede exceder 200 caracteres')
        
        # Validar email si no es anónimo
        if not data.get('anonymous'):
            email = data.get('email', '').strip()
            if not email:
                errors.append('Email es requerido para comentarios no anónimos')
            elif not validar_email(email):
                errors.append('Email inválido')
        
        # Validar nombre
        username = data.get('name', '').strip()
        if not username and not data.get('anonymous'):
            errors.append('Nombre es requerido para comentarios no anónimos')
        elif username and len(username) > 100:
            errors.append('Nombre no puede exceder 100 caracteres')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_content(content):
        """
        Sanitiza el contenido del comentario para prevenir XSS.
        """
        # Eliminar tags HTML peligrosos
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<object[^>]*>.*?</object>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<embed[^>]*>.*?</embed>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Eliminar event handlers
        content = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # Eliminar javascript:
        content = re.sub(r'javascript\s*:', '', content, flags=re.IGNORECASE)
        
        # Limitar longitud
        if len(content) > 2000:
            content = content[:2000]
        
        return content.strip()
    
    @staticmethod
    def create_comment(data, ip_address=None, user_agent=None):
        """
        Crea un nuevo comentario.
        
        Args:
            data: dict con datos del comentario
            ip_address: IP del usuario
            user_agent: User agent del navegador
            
        Returns:
            dict: {'success': bool, 'comment': Comment or None, 'errors': list}
        """
        # Validar datos
        is_valid, errors = CommentService.validate_comment_data(data)
        
        if not is_valid:
            return {'success': False, 'errors': errors}
        
        # Sanitizar contenido
        content = CommentService.sanitize_content(data.get('content', ''))
        title = sanitizar_input(data.get('title', ''), 200) if data.get('title') else None
        username = sanitizar_input(data.get('name', ''), 100) if not data.get('anonymous') else None
        email = sanitizar_input(data.get('email', ''), 120).lower() if not data.get('anonymous') else None
        
        # Crear comentario
        comment = Comment(
            username=username,
            email=email,
            rating=data.get('rating'),
            title=title,
            content=content,
            status='pending',  # Requiere aprobación
            is_anonymous=data.get('anonymous', False),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return {
            'success': True,
            'comment': comment,
            'errors': []
        }
    
    @staticmethod
    def get_approved_comments(limit=20, offset=0):
        """
        Obtiene comentarios aprobados.
        
        Returns:
            list: Lista de comentarios en formato dict
        """
        comments = Comment.query.filter_by(status='approved')\
            .order_by(Comment.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [c.to_dict() for c in comments]
    
    @staticmethod
    def get_comment_stats():
        """
        Obtiene estadísticas de comentarios.
        
        Returns:
            dict: Estadísticas
        """
        total = Comment.query.filter_by(status='approved').count()
        
        # Promedio de rating
        from sqlalchemy import func
        avg_rating = db.session.query(func.avg(Comment.rating))\
            .filter_by(status='approved')\
            .scalar() or 0
        
        # Distribución de ratings
        rating_dist = db.session.query(Comment.rating, func.count(Comment.id))\
            .filter_by(status='approved')\
            .group_by(Comment.rating)\
            .all()
        
        rating_counts = {r: c for r, c in rating_dist}
        
        return {
            'total': total,
            'average_rating': round(float(avg_rating), 2),
            'rating_distribution': rating_counts
        }
    
    @staticmethod
    def approve_comment(comment_id):
        """Aprueba un comentario (admin)."""
        comment = Comment.query.get_or_404(comment_id)
        comment.status = 'approved'
        comment.approved_at = datetime.utcnow()
        db.session.commit()
        return comment
    
    @staticmethod
    def reject_comment(comment_id):
        """Rechaza un comentario (admin)."""
        comment = Comment.query.get_or_404(comment_id)
        comment.status = 'rejected'
        db.session.commit()
        return comment
    
    @staticmethod
    def delete_comment(comment_id):
        """Elimina un comentario (admin)."""
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return True