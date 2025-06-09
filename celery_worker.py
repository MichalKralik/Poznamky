import os
from app import create_app, celery, make_celery

# Force using the eventlet pool for Windows compatibility
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = create_app()
app.app_context().push()  # Add this line to ensure app context is available
celery = make_celery(app)

# Make sure tasks are imported
import app.tasks.scheduler  # Import your task modules
