# celery_app.py
from celery import Celery
from kombu import Queue

app = Celery(
    "celery_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",   # result backend
)

# Windows/Redis-friendly serialization & basics
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,          # 1 hour
    task_time_limit=60,           # hard limit per task (seconds)
    task_soft_time_limit=50,      # soft limit (optional)
    timezone="Asia/Kolkata",
    enable_utc=False,
)

# Explicitly declare queues (Celery will auto-create them in Redis)
app.conf.task_queues = (
    Queue("add_queue"),
    Queue("subtract_queue"),
    Queue("multiply_queue"),
    Queue("divide_queue"),
)

# Route each task to its own queue
app.conf.task_routes = {
    "celery_app.add": {"queue": "add_queue"},
    "celery_app.subtract": {"queue": "subtract_queue"},
    "celery_app.multiply": {"queue": "multiply_queue"},
    "celery_app.divide": {"queue": "divide_queue"},
}

# Tasks
@app.task
def add(x, y):
    return x + y

@app.task
def subtract(x, y):
    return x - y

@app.task
def multiply(x, y):
    return x * y

@app.task
def divide(x, y):
    # guard to show real errors if divide by zero
    return x / y
