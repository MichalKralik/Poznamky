from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from app import db, limiter
from app.models import User, Note
from app.utils.crypto import AESCipher

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Omezení na 5 pokusů o přihlášení za minutu (prevence brute-force)
def login():
    """API endpoint pro přihlášení a získání JWT tokenu"""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    # Načtení přihlašovacích údajů z požadavku
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    # Ověření, že byly zadány všechny údaje
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    
    # Ověření uživatele proti databázi
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Vytvoření JWT access tokenu pro autentizaci dalších požadavků
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

@api.route('/notes', methods=['GET'])
@jwt_required()  # Vyžaduje platný JWT token
@limiter.limit("60 per minute")  # Omezení počtu požadavků
def get_notes():
    """API endpoint pro získání seznamu poznámek přihlášeného uživatele"""
    # Získání ID uživatele z JWT tokenu
    user_id = get_jwt_identity()
    notes = Note.query.filter_by(user_id=user_id, is_one_time=False).all()
    
    # Odfiltrování expirovaných poznámek
    active_notes = [note for note in notes if not note.is_expired]
    
    # Vytvoření seznamu poznámek ve formátu JSON
    result = []
    for note in active_notes:
        result.append({
            'id': note.id,
            'created_at': note.created_at.isoformat(),
            'expires_at': note.expires_at.isoformat() if note.expires_at else None,
            'is_one_time': note.is_one_time
        })
    
    return jsonify(notes=result), 200

@api.route('/notes/<int:id>', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
def get_note(id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=id, user_id=user_id).first()
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    if note.is_expired:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"error": "Note has expired"}), 410
    
    # Decrypt the note content
    cipher = AESCipher()
    decrypted_content = cipher.decrypt(note.encrypted_content, note.iv)
    
    # If it's a one-time note, mark it as read
    if note.is_one_time:
        note.mark_as_read()
    
    result = {
        'id': note.id,
        'content': decrypted_content,
        'created_at': note.created_at.isoformat(),
        'expires_at': note.expires_at.isoformat() if note.expires_at else None,
        'is_one_time': note.is_one_time
    }
    
    return jsonify(note=result), 200

@api.route('/notes', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def create_note():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400
    
    content = data.get('content')
    expiration = data.get('expiration', 'day')
    is_one_time = data.get('is_one_time', False)
    
    # Set expiration time
    expires_at = None
    if expiration != 'never':
        if expiration in current_app.config['EXPIRATION_OPTIONS']:
            seconds = current_app.config['EXPIRATION_OPTIONS'][expiration]
            expires_at = datetime.utcnow() + timedelta(seconds=seconds)
    
    # Encrypt the content
    cipher = AESCipher()
    encrypted_content, iv = cipher.encrypt(content)
    
    # Create the note
    note = Note(
        encrypted_content=encrypted_content,
        iv=iv,
        expires_at=expires_at,
        is_one_time=is_one_time,
        user_id=user_id
    )
    db.session.add(note)
    db.session.commit()
    
    result = {
        'id': note.id,
        'unique_id': note.unique_id,
        'created_at': note.created_at.isoformat(),
        'expires_at': note.expires_at.isoformat() if note.expires_at else None,
        'is_one_time': note.is_one_time
    }
    
    return jsonify(note=result), 201

@api.route('/notes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_note(id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=id, user_id=user_id).first()
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({"message": "Note deleted successfully"}), 200
