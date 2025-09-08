from .celery_app import app as celery_app

# # Expose Celery instance globally
# For dev commit all lines on this file
__all__ = ("celery_app",)