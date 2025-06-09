from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Note
from app.forms.notes import CreateNoteForm
from app.utils.crypto import AESCipher

notes = Blueprint('notes', __name__)

@notes.route('/')
@login_required
def index():
    user_notes = Note.query.filter_by(user_id=current_user.id, is_one_time=False).all()
    # Filter out expired notes from the view
    active_notes = [note for note in user_notes if not note.is_expired]
    return render_template('notes/index.html', notes=active_notes)

@notes.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateNoteForm()
    if form.validate_on_submit():
        # Set expiration time
        expires_at = None
        if form.expiration.data != 'never':
            seconds = current_app.config['EXPIRATION_OPTIONS'][form.expiration.data]
            expires_at = datetime.utcnow() + timedelta(seconds=seconds)
        
        # Encrypt the content
        cipher = AESCipher()
        encrypted_content, iv = cipher.encrypt(form.content.data)
        
        # Create the note
        note = Note(
            encrypted_content=encrypted_content,
            iv=iv,
            expires_at=expires_at,
            is_one_time=form.is_one_time.data,
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        
        if form.is_one_time.data:
            flash(f'One-time note created! Share this link: {url_for("notes.view_shared", unique_id=note.unique_id, _external=True)}')
        else:
            flash('Note created successfully!')
        return redirect(url_for('notes.index'))
    
    return render_template('notes/create.html', form=form)

@notes.route('/view/<int:id>')
@login_required
def view(id):
    note = Note.query.get_or_404(id)
    
    # Check if the note belongs to the current user
    if note.user_id != current_user.id:
        abort(403)
    
    # Check if the note has expired
    if note.is_expired:
        db.session.delete(note)
        db.session.commit()
        flash('This note has expired and has been deleted.')
        return redirect(url_for('notes.index'))
    
    # Decrypt the note content
    cipher = AESCipher()
    decrypted_content = cipher.decrypt(note.encrypted_content, note.iv)
    
    # If it's a one-time note, mark it as read
    if note.is_one_time:
        note.mark_as_read()
    
    return render_template('notes/view.html', note=note, content=decrypted_content)

@notes.route('/shared/<unique_id>')
def view_shared(unique_id):
    note = Note.query.filter_by(unique_id=unique_id).first_or_404()
    
    # Check if the note has expired
    if note.is_expired:
        db.session.delete(note)
        db.session.commit()
        flash('This note has expired or has already been read.')
        return redirect(url_for('auth.login'))
    
    # Decrypt the note content
    cipher = AESCipher()
    decrypted_content = cipher.decrypt(note.encrypted_content, note.iv)
    
    # If it's a one-time note, mark it as read
    if note.is_one_time:
        note.mark_as_read()
        flash('This is a one-time note and will be deleted after you close it.')
    
    return render_template('notes/shared.html', note=note, content=decrypted_content)

@notes.route('/delete/<int:id>')
@login_required
def delete(id):
    note = Note.query.get_or_404(id)
    
    # Check if the note belongs to the current user
    if note.user_id != current_user.id:
        abort(403)
    
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!')
    return redirect(url_for('notes.index'))
