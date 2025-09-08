from tasks import meesho_generate_gstr ,flipcart_generate_gstr ,limeroad_generate_gstr , snapdeal_generate_gstr , myntra_generate_gstr , ajio_generate_gstr
from celery import Celery
from celery.exceptions import Reject
import crontab

app = Celery(
    "my_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

TASK_MAPPING = {
    "meesho" : meesho_generate_gstr,
    "flipcart" : flipcart_generate_gstr,
    "snapdeal" : snapdeal_generate_gstr,
    "ajio" : ajio_generate_gstr,
    "myntra" : myntra_generate_gstr,
    "limeroad": limeroad_generate_gstr
}

# WORKING_JOBS = ["meesho",
#                 "flipcart",
#                 "snapdeal",
#                 "ajio",
#                 "myntra",
#                 "limeroad"]

app.conf.task_queues = {
    # meesho 
    'meesho_queue': {
        'exchange': 'priority_exchange',
        'routing_key': 'priority_key',
    },
    
    # flipcart
    'flipcart_queue': {
        'exchange': 'normal_exchange',
        'routing_key': 'normal_key',
    },
    
    # limeroad
    'limeroad_queue': {
        'exchange': 'normal_exchange',
        'routing_key': 'normal_key',
    },

    # myntra
    'myntra_queue': {
        'exchange': 'normal_exchange',
        'routing_key': 'normal_key',
    },

    # snapdeal
    'snapdeal_queue': {
        'exchange': 'normal_exchange',
        'routing_key': 'normal_key',
    },

    # ajio
    'ajio_queue': {
        'exchange': 'normal_exchange',
        'routing_key': 'normal_key',
    },
    
    'task_update_queue': {
        'exchange': 'normal_exchange',
        'routing_key': 'normal_key',
    },
}





def route_task(name, args, kwargs, options, task=None, **kw):
    """
    Route tasks based on user type.
    """
    marketplace_name = kwargs.get('marketplace_name')

    if marketplace_name:
        # daily sync orders
        if 'meesho' in marketplace_name:
            return {'queue': 'meesho_queue'}

        # amazon payment sync by api
        elif "flipcart" in marketplace_name:
            return {'queue': 'flipcart_queue'}

        # amazon payment sync by api
        elif "ajio" in marketplace_name:
            return {'queue': 'ajio_queue'}

        # amazon payment sync by file
        elif "myntra" in marketplace_name:
            return {'queue': 'myntra_queue'}

        # meesho payment sync by file
        elif "snapdeal" in marketplace_name:
            return {'queue': 'snapdeal_queue'}

        # flipkart payment sync by file
        elif "limeroad" in marketplace_name:
            return {'queue': 'limeroad_queue'}

        # myntra payment sync by file
        elif marketplace_name == 'update_task':
            return {'queue': 'task_update_queue'}

        


    return {'queue': 'light_task_queue'}


app.conf.task_routes = (route_task,)

def get_task_status_by_uuid(task_id):
    """
    Get the status of a task by its UUID (task_id).
    This function checks if the task is currently running or if it has completed.
    """
    i = app.control.inspect()

    try:
        # Get active tasks from workers
        active_tasks = i.active()
        reserved_tasks = i.reserved()
        scheduled_tasks = i.scheduled()

        # Look through active tasks to find the task with the matching task_id
        for worker, tasks in active_tasks.items():
            for task in tasks:
                if task['id'] == task_id:
                    return {'status': 'running', 'found': True, 'task': task}


        for worker, tasks in reserved_tasks.items():
            for task in tasks:
                if task['id'] == task_id:
                    return {'status': 'reserved', 'found': True, 'task': task}

        for worker, tasks in scheduled_tasks.items():
            for task in tasks:
                if task['id'] == task_id:
                    return {'status': 'scheduled', 'found': True, 'task': task}

        return {'status': 'not found', 'found': False, 'task': None}

    except Exception as e:
        print(f"Unexpected error occurred while fetching task status for task_id {task_id}: {str(e)}")
        return {'status': 'error', 'found': False, 'task': None}

def add_task_into_queue(task):
    job_id = task["id"]
    user_id = task["user_id"][0]
    marketplace_name = task["marketplace_name"]
    job_status = task["job_status"]
    # isDebug = task.get("x_is_debug", False)
    payload = task["payload"]
    # payload["file_key"] = task["file_key"]

    if marketplace_name in TASK_MAPPING:
        existing_task_details = get_task_status_by_uuid(job_id)
        # SKIP_BLOCKIG.get(job_type)

        if not existing_task_details["found"]:
            result = TASK_MAPPING[marketplace_name].apply_async(
                args=[payload],  # Pass the payload as an argument
                kwargs={"user_id": user_id, "marketplace_name": marketplace_name, "job_id": job_id, "job_status": job_status,},
                task_id=str(job_id),  # Use job_id as task_id
            )
        else:
            print("add_task_into_queue failed")
            
    
# @app.task(queue='task_update_queue', max_retries=1, task_acks_late=True)
# def assign_jobs_v2():

#     try:

#         job_types = [
#             'meesho',
#             'flipcart',
#             'limeroad',
#             'snapdeal',
#             'ajio',
#             'myntra',
#         ]

#         pending_jobs = []

#         for job_type in job_types:
#             domain = [
#                 ("job_status", "=", "pending"),
#                 ("job_type", "=", job_type),
#                 ("worker_type", "=", WORKER_TYPE),
#             ]
#             jobs = odoo_client.search_read(
#                 "job.work",
#                 domain,
#                 fields=[],
#                 limit=200
#             )
#             if jobs:
#                 pending_jobs.extend(jobs)

#         commonlogger.info(f"pending_jobs {pending_jobs}")

#         batch_tasks = []

#         for task in pending_jobs:
#             job_id = task["id"]
#             user_id = task["user_id"][0]
#             job_type = task["job_type"]
#             job_status = task["job_status"]
#             isDebug = task.get("x_is_debug", False)
#             payload = task["payload"]
#             payload["file_key"] = task.get("file_key")

#             # Check if job_type exists in mapping
#             if job_type in TASK_MAPPING:
#                 signature = TASK_MAPPING[job_type].s(
#                     payload,
#                     user_id=user_id,
#                     job_type=job_type,
#                     job_id=job_id,
#                     job_status=job_status,
#                     isDebug=isDebug
#                 ).set(task_id=str(job_id))

#                 batch_tasks.append(signature)

#                 # optionally update Odoo status immediately
#                 # comment out if you want to update only after tasks run
#                 common_odoo_client.update_work_status(
#                     work_id=job_id,
#                     status="in_queue",
#                     celery_job_id=str(job_id)
#                 )
#             else:
#                 commonlogger.info(f"Invalid Task {task}")

#         if batch_tasks:
#             commonlogger.info(f"Dispatching group of {len(batch_tasks)} tasks...")
#             group(batch_tasks).apply_async()

#     except Exception as e:
#         commonlogger.info(f"Error in task success callback: {e}")
#         raise Reject("Error in task success callback", requeue=False)








@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #commen Worker
    sender.add_periodic_task(
        crontab(hour=15, minute=44, day_of_week=''),  # Schedule for midnight
        meesho_gstr_generate,  # Your new task
        name='testing_task'
        )



@app.task(queue='meesho_queue', max_retries=0, ignore_result=False)
def meesho_gstr_generate():
    try:
        """
        Runs a local task without Odoo or user dependencies.
        Replace `your_local_function()` with your actual logic.
        """
        tasks = []
        
        meesho_payload = {"marketplace_name" : "meesho" ,
           "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\meesho\Input_file\tcs_sales.xlsx",
            r"C:\Users\st\Desktop\Rachit\GST_format\meesho\Input_file\tcs_sales_return.xlsx"
        ],
           "user_email" : "rachit" ,
           }

        print("Called Function")
        
        # Example: call your local function(s) to generate tasks
        tasks = meesho_generate_gstr(meesho_payload)  
        print("paylaod passed")

        # For debugging, just print the tasks
        print(f"Tasks prepared: {tasks}")

        return {"status": "success", "count": len(tasks), "message": "success"}

    except Exception as e:
        print(f"Error in task: {e}")
        raise Reject("Error in task callback", requeue=False)


@app.task(queue='flipcart_queue', max_retries=0, ignore_result=False)
def flipcart_gstr_generate():
    try:
        """
        Runs a local task without Odoo or user dependencies.
        Replace `your_local_function()` with your actual logic.
        """
        tasks = []
        
        flipcart_payload = {"marketplace_name" : "flipcart" ,
        "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\Flipcart\input_files\sales_report.xlsx"
        ],
            "user_email" : "rachit" ,
            }

        # Example: call your local function(s) to generate tasks
        tasks = flipcart_generate_gstr(flipcart_payload)  

        # For debugging, just print the tasks
        print(f"Tasks prepared: {tasks}")

        return {"status": "success", "count": len(tasks), "message": "success"}

    except Exception as e:
        print(f"Error in task: {e}")
        raise Reject("Error in task callback", requeue=False)


@app.task(queue='myntra_queue', max_retries=0, ignore_result=False)
def myntra_gstr_generate():
    try:
        """
        Runs a local task without Odoo or user dependencies.
        Replace `your_local_function()` with your actual logic.
        """
        tasks = []
        
        myntra_payload = {"marketplace_name" : "myntra" ,
                "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\packed.csv",
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\rt.csv",
            r"C:\Users\st\Desktop\Rachit\GST_format\myntra\Input_files\rto.csv"
        ],
                    "user_email" : "rachit" ,
            }

        # Example: call your local function(s) to generate tasks
        tasks = myntra_generate_gstr(myntra_payload)  

        # For debugging, just print the tasks
        print(f"Tasks prepared: {tasks}")

        return {"status": "success", "count": len(tasks), "message": "success"}

    except Exception as e:
        print(f"Error in task: {e}")
        raise Reject("Error in task callback", requeue=False)

@app.task(queue='limeroad_queue', max_retries=0, ignore_result=False)
def limeroad_gstr_generate():
    try:
        """
        Runs a local task without Odoo or user dependencies.
        Replace `your_local_function()` with your actual logic.
        """
        
        limeroad_payload = {"marketplace_name" : "limeroad" ,
           "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\Limeroad\input_files\limeroad_report.xlsx"
        ],
           "user_email" : "rachit" ,
           }
        
        tasks = []

        # Example: call your local function(s) to generate tasks
        tasks = limeroad_generate_gstr(limeroad_payload)  

        # For debugging, just print the tasks
        print(f"Tasks prepared: {tasks}")

        return {"status": "success", "count": len(tasks), "message": "success"}

    except Exception as e:
        print(f"Error in task: {e}")
        raise Reject("Error in task callback", requeue=False)

@app.task(queue='ajio_queue', max_retries=0, ignore_result=False)
def ajio_gstr_generate():
    try:
        """
        Runs a local task without Odoo or user dependencies.
        Replace `your_local_function()` with your actual logic.
        """
        tasks = []

        ajio_payload = {"marketplace_name" : "ajio" ,
                "files": [
            r"C:\Users\st\Desktop\Rachit\GST_format\ajio\input_files\DropShipGstReports.xlsx",
            r"C:\Users\st\Desktop\Rachit\GST_format\ajio\input_files\DropShipRtvReports.xlsx"
        ],
                    "user_email" : "rachit" ,
            }
        
        # Example: call your local function(s) to generate tasks
        tasks = ajio_generate_gstr(ajio_payload)  

        # For debugging, just print the tasks
        print(f"Tasks prepared: {tasks}")

        return {"status": "success", "count": len(tasks), "message": "success"}

    except Exception as e:
        print(f"Error in task: {e}")
        raise Reject("Error in task callback", requeue=False)


@app.task(queue='snapdeal_queue', max_retries=0, ignore_result=False)
def snapdeal_gstr_generate():
    try:
        """
        Runs a local task without Odoo or user dependencies.
        Replace `your_local_function()` with your actual logic.
        """
        tasks = []
        
        snapdeal_payload = {"marketplace_name" : "snapdeal" ,
                    "files": [r"C:\Users\st\Desktop\Rachit\GST_format\Snapdeal\input_files\snapdeal_sales.xlsx"],
                    "user_email" : "rachit" ,
            }

        # Example: call your local function(s) to generate tasks
        tasks = snapdeal_generate_gstr(snapdeal_payload)  

        # For debugging, just print the tasks
        print(f"Tasks prepared: {tasks}")

        return {"status": "success", "count": len(tasks), "message": "success"}

    except Exception as e:
        print(f"Error in task: {e}")
        raise Reject("Error in task callback", requeue=False)


app.autodiscover_tasks(["celery_app.tasks"])






# Additional settings
# app.conf.task_serializer = "json"
# app.conf.result_serializer = "json"
# app.conf.accept_content = ["json"]
# app.conf.timezone = "Asia/Kolkata"
# app.conf.enable_utc = True
# app.conf.broker_connection_retry_on_startup = True
# app.conf.task_ignore_result = False
# app.conf.worker_send_task_events = True
# app.conf.worker_pool_restarts = True



if __name__ == "__main__":
    pass
    