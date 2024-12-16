import logging
import yagmail


YAGMAIL_USER = "super.avel-2014@yandex.ru"
YAGMAIL_PASSWORD = "tjvewrgsehvgdsqj"
logger = logging.getLogger(__name__)


def send_confirmation_email(email, access_token):
    sender_email = YAGMAIL_USER
    sender_password = YAGMAIL_PASSWORD
    if not sender_email or not sender_password:
        logger.error("EMAIL_SENDER or EMAIL_PASSWORD not set!")
        return

    try:
        yag = yagmail.SMTP(
            sender_email,
            sender_password,
            host="smtp.yandex.ru",
            port=465,
            smtp_ssl=True,
        )
        subject = "Подтверждение регистрации"
        body = f"""
        Спасибо за регистрацию!
        Ваш код доступа: {access_token}
        """
        yag.send(to=email, subject=subject, contents=body)
        logger.info(f"Письмо отправлено на {email}")
    except Exception as e:
        logger.exception(f"Ошибка отправки письма: {e}")
