from celery import Celery

celery = Celery("tasks", broker="amqp://guest:guest@rabbitmq:5672//")

celery.conf.update(
    result_backend="rpc://",
)

if __name__ == "__main__":
    celery.start()
