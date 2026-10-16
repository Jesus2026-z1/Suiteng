"""
Aplicación principal - Fábrica de aplicación Flask.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import config_by_name
from extensions import db, mail, oauth, limiter, init_limiter
from routes import register_blueprints
from security import crear_admin_inicial
from datetime import datetime


def create_app(config_name=None):
    """Fábrica de aplicación Flask."""
    if config_name is None:
        config_name = 'default'
    
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config_by_name[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    init_limiter(app)
    
    # Configurar CORS
    CORS(app, 
         supports_credentials=True, 
         origins=[app.config['FRONTEND_URL']],
         methods=['GET', 'POST', 'PUT', 'DELETE'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Configurar OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        authorize_url='https://github.com/login/oauth/authorize',
        token_url='https://github.com/login/oauth/access_token',
        client_kwargs={'scope': 'user:email'}
    )
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Headers de seguridad
    @app.after_request
    def set_security_headers(response):
        """Agrega headers de seguridad."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Verifica que el backend esté funcionando."""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    
    # Crear tablas y admin inicial
    with app.app_context():
        db.create_all()
        crear_admin_inicial()
    
    return app


# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("Backend Seguro - Sistema de Análisis")
    print("=" * 60)
    print(f"Servidor: http://localhost:5000")
    print(f"Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 60)
    
    # En producción, usar gunicorn o waitress
    app.run(debug=False, host='0.0.0.0', port=5000)