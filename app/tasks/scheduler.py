from datetime import datetime
from celery.schedules import crontab
from app import celery, db
from app.models import Note

@celery.task
def delete_expired_notes():
    """Delete all notes that have expired"""
    now = datetime.utcnow()
    
    # Find notes that have reached their expiration time
    expired_by_time = Note.query.filter(
        Note.expires_at.isnot(None),
        Note.expires_at <= now
    ).all()
    
    # Find one-time notes that have been read
    expired_one_time = Note.query.filter_by(
        is_one_time=True,
        was_read=True
    ).all()
    
    # Delete all expired notes
    count = 0
    for note in expired_by_time + expired_one_time:
        db.session.delete(note)
        count += 1
    
    db.session.commit()
    return f"Deleted {count} expired notes"

# Schedule the task to run every hour
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour='*'),  # Run at the start of every hour
        delete_expired_notes.s(),
        name='delete expired notes every hour'
    )
