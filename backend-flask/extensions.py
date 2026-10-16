"""
Inicialización de extensiones de Flask.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth

# Inicializar extensiones
db = SQLAlchemy()
mail = Mail()
oauth = OAuth()

# Rate limiter (se inicializa en create_app)
limiter = None

def init_limiter(app):
    """Inicializa el rate limiter con la app."""
    global limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    return limiter