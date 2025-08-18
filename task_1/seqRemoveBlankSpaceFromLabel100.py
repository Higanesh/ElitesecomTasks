import fitz                # PyMuPDF
import random              # For random numbers
from io import BytesIO     # For PDF bytes
import requests            # For downloading PDFs
import time                # For timing
import psutil              # For monitoring system resources
import os

# -------------------------------
# Start overall execution timer
# -------------------------------
overall_start = time.perf_counter()

# Create an empty PDF object to store all processed pages
merged_pdf = fitz.open()

# Track execution times
download_time = 0.0
merge_time = 0.0

# Get current process for monitoring
process = psutil.Process(os.getpid())

def print_usage(tag=""):
    """Print current CPU and memory usage"""
    mem_info = process.memory_info().rss / (1024 * 1024)  # in MB
    cpu_percent = process.cpu_percent(interval=0.1)       # CPU %
    print(f"🔹 {tag} | CPU: {cpu_percent:.2f}% | RAM: {mem_info:.2f} MB")

# -------------------------------
# Process 100 PDFs
# -------------------------------
for i in range(100):
    pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"

    # Step 1: Download PDF
    t1 = time.perf_counter()
    response = requests.get(pdf_url)
    t2 = time.perf_counter()
    download_time += (t2 - t1)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to download {pdf_url}")

    pdf_bytes = BytesIO(response.content)

    # Step 2: Process PDF
    t3 = time.perf_counter()
    doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")
    page = doc[0]

    blocks = page.get_text("blocks")
    if not blocks:
        raise Exception("❌ No text found in PDF.")

    first_block = min(blocks, key=lambda b: b[1])
    last_block = max(blocks, key=lambda b: b[3])

    # Insert random text top
    random_top_text = "Random Top Text: " + str(random.randint(1000, 9999))
    page.insert_text((page.rect.x0 + 12, first_block[1] - 5),
                     random_top_text, fontsize=12, fontname="helv", fill=(0, 0, 0))

    # Insert random text bottom
    random_bottom_text = "Random Bottom Text: " + str(random.randint(1000, 9999))
    page.insert_text((page.rect.x0 + 12, last_block[3] + 15),
                     random_bottom_text, fontsize=12, fontname="helv", fill=(0, 0, 0))

    # Crop bottom blank space
    blocks_after = page.get_text("blocks")
    last_y_after = max(b[3] for b in blocks_after)
    crop_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_y_after + 5)
    page.set_cropbox(crop_rect)

    merged_pdf.insert_pdf(doc)
    t4 = time.perf_counter()
    merge_time += (t4 - t3)

    # Print system usage every 10 PDFs
    if (i + 1) % 10 == 0:
        print_usage(tag=f"After {i+1} PDFs")

# Step 3: Save merged PDF
output_pdf = r"D:\myProjects\ElitesecomTasks\Output PDFs\removeBlankSpaceMergeAll.pdf"
merged_pdf.save(output_pdf)
merged_pdf.close()

# Step 4: End timing
overall_end = time.perf_counter()
total_time = overall_end - overall_start

# -------------------------------
# Final results
# -------------------------------
print(f"\n⏬ Total download time: {download_time:.2f} seconds")
print(f"✍️ Total processing + merging time: {merge_time:.2f} seconds")
print(f"⏱ Overall total time: {total_time:.2f} seconds")
print(f"➡️ Average time per PDF: {total_time/100:.2f} seconds")

# Final usage snapshot
print_usage(tag="Final Resource Usage")
