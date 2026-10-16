"""
Registro de blueprints.
"""
from routes.auth import auth_bp
from routes.oauth import oauth_bp
from routes.users import users_bp
from routes.admin import admin_bp
from routes.donations import donations_bp
from routes.comments import comments_bp  # ← NUEVO

def register_blueprints(app):
    """Registra todos los blueprints en la aplicación."""
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(oauth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(donations_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')  # ← NUEVO