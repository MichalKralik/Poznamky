from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from config import Config

# Inicializace Flask rozšíření - tyto objekty budou později připojeny k Flask aplikaci
db = SQLAlchemy()  # Databázové ORM pro práci s databází
migrate = Migrate()  # Správa databázových migrací
login_manager = LoginManager()  # Správa přihlášení uživatelů
jwt = JWTManager()  # JWT autentizace pro API
csrf = CSRFProtect()  # Ochrana proti CSRF útokům
limiter = Limiter(
    key_func=get_remote_address,  # Identifikace uživatelů podle IP adresy
    default_limits=["200 per day", "50 per hour"]  # Výchozí limity pro rate limiting
)

# Inicializace Celery pro background tasky
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    """Factory pattern pro vytvoření a konfiguraci Flask aplikace"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializace rozšíření s aplikací
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Kam přesměrovat nepřihlášené uživatele
    jwt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    celery.conf.update(app.config)
    
    # Registrace blueprintů - modulární části aplikace
    from app.routes.auth import auth as auth_blueprint
    from app.routes.notes import notes as notes_blueprint
    from app.routes.api import api as api_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(notes_blueprint)
    app.register_blueprint(api_blueprint)
    
    return app

# Konfigurace Celery pro práci s Flask kontextem
def make_celery(app):
    """Vytvoří Celery objekt, který správně pracuje s Flask kontextem aplikace"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Zajišťuje, že Celery tasky mají přístup k Flask kontextu aplikace"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
