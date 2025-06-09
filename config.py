import os
from datetime import timedelta

class Config:
    """Konfigurační třída pro Flask aplikaci"""
    # Tajný klíč pro zabezpečení session a CSRF tokenů
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Databázové připojení
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT nastavení pro API
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Redis a Celery nastavení pro background tasky
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Šifrovací klíč pro AES-256
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'default-encryption-key'
    
    # Možnosti expirace poznámek (v sekundách)
    EXPIRATION_OPTIONS = {
        'hour': 3600,
        'day': 86400,
        'week': 604800
    }

    # Nastavení pro testování - umožňuje spustit Celery tasky okamžitě bez workeru
    TESTING = os.environ.get('TESTING', 'False') == 'True'
    CELERY_TASK_ALWAYS_EAGER = TESTING  # Spouštět tasky okamžitě bez Celery workeru
