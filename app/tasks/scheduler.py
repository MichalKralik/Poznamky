from datetime import datetime
from celery.schedules import crontab
from app import celery, db
from app.models import Note

@celery.task
def delete_expired_notes():
    """Celery task pro automatické mazání expirovaných poznámek
    
    Tento task se spouští pravidelně a maže poznámky, kterým vypršela 
    platnost nebo které jsou jednorázové a již byly přečteny.
    """
    now = datetime.utcnow()
    
    # Najde poznámky, kterým vypršel čas platnosti
    expired_by_time = Note.query.filter(
        Note.expires_at.isnot(None),
        Note.expires_at <= now
    ).all()
    
    # Najde jednorázové poznámky, které už byly přečteny
    expired_one_time = Note.query.filter_by(
        is_one_time=True,
        was_read=True
    ).all()
    
    # Smaže všechny expirované poznámky
    count = 0
    for note in expired_by_time + expired_one_time:
        db.session.delete(note)
        count += 1
    
    db.session.commit()
    return f"Deleted {count} expired notes"

# Nastavení plánovače pro spouštění tasku každou hodinu
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Konfigurace periodických úloh Celery
    
    Nastaví úlohu mazání expirovaných poznámek na každou hodinu.
    """
    sender.add_periodic_task(
        crontab(minute=0, hour='*'),  # Spouštět na začátku každé hodiny
        delete_expired_notes.s(),
        name='delete expired notes every hour'
    )
