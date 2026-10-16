"""
Configuración de la aplicación.
"""
import os
from datetime import timedelta

class Config:
    """Configuración base."""
    # Clave secreta
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///usuarios.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(32).hex())
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # URLs
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8080')
    
    # OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    
    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@ejemplo.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin123!')


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False


# Diccionario de configuraciones
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}