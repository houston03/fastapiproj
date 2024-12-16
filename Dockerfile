FROM python:3.13-alpine

# Зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Приложение
COPY . /app

# Рабочую директория
WORKDIR /app

# Скрипты на создание миграций
RUN chmod +x apply_migrations.sh wait_for_db.sh

# Запуск приложения
ENV WORKERS_COUNT=4
ENV TIMEOUT_SECONDS=120
CMD ["./wait_for_db.sh", "db", "sh", "-c", "alembic upgrade head && gunicorn main:app --bind 0.0.0.0:8000 --workers ${WORKERS_COUNT} --worker-class uvicorn.workers.UvicornWorker --timeout ${TIMEOUT_SECONDS}"]