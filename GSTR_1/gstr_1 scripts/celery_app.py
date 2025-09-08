from celery import Celery
from kombu import Queue
from myntra_gst1 import MyntraGstr1Processor
from limeroad_gst1 import LimeroadGSTProcessor
from ajio_gst1 import AjioGSTR1Processor
from workbook import ExcelWriter

app = Celery(
    "celery_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=False,
)

# Define queues
app.conf.task_queues = (
    Queue("myntra_queue"),
    Queue("limeroad_queue"),
    Queue("ajio_queue"),
)

# Task routes
app.conf.task_routes = {
    "myntra_gst1.run_myntra_gstr1": {"queue": "myntra_queue"},
    "limeroad_gst1.run_limeroad_gstr1": {"queue": "limeroad_queue"},
    "ajio_gst1.run_ajio_gstr1": {"queue": "ajio_queue"},
}


# Marketplace tasks
@app.task
def run_myntra_gstr1(packed_file, rt_file=None, rto_file=None, output_file=None):
    processor = MyntraGstr1Processor(packed_file, rt_file, rto_file)
    data = processor.process_data()

    if output_file:
        excel_writer = ExcelWriter(output_file, "B2CS Summary")
        excel_writer.write_data(data)
        excel_writer.save()

    return f"✅ Myntra GSTR-1 report created at {output_file}"

@app.task
def run_limeroad_gstr1(input_file, output_file=None):
    processor = LimeroadGSTProcessor(input_file)
    data = processor.process()

    if output_file:
        excel_writer = ExcelWriter(output_file, "B2CS Summary")
        excel_writer.write_data(data)
        excel_writer.save()

    return f"✅ Limeroad GSTR-1 report created at {output_file}"

@app.task
def run_ajio_gstr1(gst_file, rtv_file=None, output_file=None):
    processor = AjioGSTR1Processor(gst_file, rtv_file)  # your Ajio class
    data = processor.process()

    if output_file:
        excel_writer = ExcelWriter(output_file, "B2B Summary")
        excel_writer.write_data(data["b2b"])
        excel_writer.add_sheet("CDNR", data["cdnr"])
        excel_writer.save()

    return f"✅ Ajio GSTR-1 report created at {output_file}"