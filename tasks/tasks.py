from src.app.api.email import send_confirmation_email
from tasks.celeryconfig import celery as celery_app  # Импортируйте celery из celery.py


@celery_app.task
def send_confirmation_email_task(email, access_token):
    send_confirmation_email(email, access_token)
