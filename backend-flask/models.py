"""
Modelos de base de datos.
"""
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    """Modelo de usuario seguro."""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), default='usuario', nullable=False)
    activo = db.Column(db.Boolean, default=True)
    email_verificado = db.Column(db.Boolean, default=False)
    
    # OAuth
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    github_id = db.Column(db.String(100), unique=True, nullable=True)
    
    # Seguridad
    ultimo_login = db.Column(db.DateTime, nullable=True)
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    token_verificacion = db.Column(db.String(100), nullable=True)
    token_reset = db.Column(db.String(100), nullable=True)
    token_reset_expira = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Permisos
    paginas_permitidas = db.Column(db.Text, default='Minimos_Cuadrados')
    
    def set_password(self, password):
        """Hashea la contraseña con PBKDF2-SHA256."""
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256', 
            salt_length=16
        )
    
    def check_password(self, password):
        """Verifica la contraseña."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convierte a diccionario (sin datos sensibles)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'activo': self.activo,
            'email_verificado': self.email_verificado,
            'paginas_permitidas': self.paginas_permitidas,
            'fecha_registro': self.fecha_registro.isoformat()
        }


class TokenBloqueado(db.Model):
    """Lista negra de tokens JWT."""
    __tablename__ = 'tokens_bloqueados'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)


class LogAuditoria(db.Model):
    """Logs de seguridad."""
    __tablename__ = 'logs_auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(80), nullable=True)
    evento = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)
    detalles = db.Column(db.Text, nullable=True)

class Donation(db.Model):
    """Modelo de donativos."""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    username = db.Column(db.String(80), nullable=True)  # Para donativos anónimos
    email = db.Column(db.String(120), nullable=True)
    
    # Monto y moneda
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='USD')  # USD, EUR, MXN, BTC, ETH, etc.
    amount_usd = db.Column(db.Float, nullable=False)  # Valor convertido a USD
    
    # Método de pago
    payment_method = db.Column(db.String(20), nullable=False)  # paypal, bitcoin, ethereum, usdt
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    transaction_id = db.Column(db.String(100), nullable=True)
    
    # Información adicional
    is_anonymous = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    user = db.relationship('Usuario', backref=db.backref('donations', lazy=True))
    
    def to_dict(self):
        """Convierte a diccionario."""
        display_name = "Anónimo" if self.is_anonymous else (self.username or "Donante")
        return {
            'id': self.id,
            'donor': display_name,
            'amount': self.amount,
            'currency': self.currency,
            'amount_usd': self.amount_usd,
            'payment_method': self.payment_method,
            'date': self.created_at.isoformat(),
            'message': self.message
        }

class Comment(db.Model):
    """Modelo de comentarios."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    username = db.Column(db.String(80), nullable=True)  # Para comentarios anónimos
    email = db.Column(db.String(120), nullable=True)
    
    # Contenido
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrellas
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    
    # Moderación
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_anonymous = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = db.relationship('Usuario', backref=db.backref('comments', lazy=True))
    
    def to_dict(self, include_email=False):
        """Convierte a diccionario."""
        display_name = "Anónimo" if self.is_anonymous else (self.username or "Usuario")
        result = {
            'id': self.id,
            'author': display_name,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'date': self.created_at.isoformat(),
            'is_anonymous': self.is_anonymous
        }
        
        if include_email and self.email:
            result['email'] = self.email
        
        return result