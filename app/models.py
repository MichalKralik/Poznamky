from datetime import datetime, timedelta
import uuid
import bcrypt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(id):
    """Funkce potřebná pro Flask-Login - načte uživatele podle ID"""
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    """Model uživatele pro databázi"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email jako jedinečný identifikátor
    password_hash = db.Column(db.String(128))  # Ukládáme pouze hash hesla, nikdy samotné heslo
    notes = db.relationship('Note', backref='author', lazy='dynamic')  # Vztah 1:N k poznámkám
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Zahashuje heslo pomocí bcrypt před uložením"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')
        
    def check_password(self, password):
        """Ověří, zda zadané heslo odpovídá uloženému hashi"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Note(db.Model):
    """Model poznámky pro databázi"""
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)  # Pro jednorázové sdílení
    encrypted_content = db.Column(db.Text, nullable=False)  # Šifrovaný obsah poznámky
    iv = db.Column(db.Text, nullable=False)  # Inicializační vektor pro AES šifrování
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Čas vytvoření
    expires_at = db.Column(db.DateTime, nullable=True)  # Čas expirace, může být null (nikdy nevyprší)
    is_one_time = db.Column(db.Boolean, default=False)  # Jednorázová poznámka?
    was_read = db.Column(db.Boolean, default=False)  # Byla poznámka přečtena?
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Propojení s uživatelem
    
    def __repr__(self):
        return f'<Note {self.id}>'
    
    @property
    def is_expired(self):
        """Zjistí, zda poznámka vypršela buď podle času nebo protože byla jednorázová a již přečtená"""
        if self.expires_at and self.expires_at <= datetime.utcnow():
            return True
        if self.is_one_time and self.was_read:
            return True
        return False
    
    def mark_as_read(self):
        """Označí poznámku jako přečtenou (důležité pro jednorázové poznámky)"""
        self.was_read = True
        db.session.commit()
