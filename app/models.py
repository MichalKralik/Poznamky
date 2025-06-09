from datetime import datetime, timedelta
import uuid
import bcrypt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Note', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    encrypted_content = db.Column(db.Text, nullable=False)
    iv = db.Column(db.Text, nullable=False)  # Initialization vector for AES
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_one_time = db.Column(db.Boolean, default=False)
    was_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Note {self.id}>'
    
    @property
    def is_expired(self):
        if self.expires_at and self.expires_at <= datetime.utcnow():
            return True
        if self.is_one_time and self.was_read:
            return True
        return False
    
    def mark_as_read(self):
        self.was_read = True
        db.session.commit()
