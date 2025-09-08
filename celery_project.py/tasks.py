# from celery import shared_task
# from celery_project.task.limeroad_gst1 import limeroad_handler
# from celery_project.task.meesho_gst1 import meesho_handler
# from celery_project.task.flipcart_gst1 import flipcart_handler
# from celery_project.task.snapdeal_gst1 import snapdeal_handler
# from celery_project.task.ajio_gst1 import ajio_handler
# from celery_project.task.myntra_gst1 import myntra_handler

from celery import shared_task
from task.limeroad_gst1 import limeroad_handler
from task.meesho_gst1 import meesho_handler
from task.flipcart_gst1 import flipcart_handler
from task.snapdeal_gst1 import snapdeal_handler
from task.ajio_gst1 import ajio_handler
from task.myntra_gst1 import myntra_handler

@shared_task(bind=True)
def meesho_generate_gstr(payload):
    try:
        result = meesho_handler(payload=payload)
        print(result)
        return result
    except Exception as e:
        raise e
    

@shared_task(bind=True)
def flipcart_generate_gstr(payload):
    try:
        result = flipcart_handler(payload=payload)
        print(result)
        return result
    except Exception as e:
        raise e
    
@shared_task(bind=True)
def limeroad_generate_gstr(payload):
    try:
        result = limeroad_handler(payload=payload)
        print(result)
        return result
    except Exception as e:
        raise e

@shared_task(bind=True)
def snapdeal_generate_gstr(payload):
    try:
        result = snapdeal_handler(payload=payload)
        print(result)
        return result
    except Exception as e:
        raise e
    

@shared_task(bind=True)
def myntra_generate_gstr(payload):
    try:
        result = myntra_handler(payload=payload)
        print(result)
        return result
    except Exception as e:
        raise e
    
@shared_task(bind=True)
def ajio_generate_gstr(payload):
    try:
        result = ajio_handler(payload=payload)
        print(result)
        return result
    except Exception as e:
        raise e