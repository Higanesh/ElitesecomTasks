import fitz
import random
import requests
import time
import psutil
import os
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

"""
PS D:\myProjects\ElitesecomTasks\task_1> py .\paraRemoveBlankSpaceFromLabel100
⏬ Total processing time (all workers): 37.75 seconds
⏱ Overall total time: 4.48 seconds
➡️ Average time per PDF: 0.04 seconds
💾 Memory Usage -> RSS: 69.04 MB | VMS: 67.62 MB
"""

# ----------- CONFIG -------------
NUM_PDFS = 100
MAX_WORKERS = 10   # Adjust based on CPU/Network
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"
output_pdf = r"D:\myProjects\ElitesecomTasks\Output PDFs\parallelMerged.pdf"
# --------------------------------

def download_and_process(i, url):
    """Download one PDF, add random text, crop blank space, return fitz.Document"""
    t1 = time.perf_counter()

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to download {url}")

    # Open PDF in memory
    doc = fitz.open(stream=response.content, filetype="pdf")
    page = doc[0]

    # Extract text blocks
    blocks = page.get_text("blocks")
    if blocks:
        first_block = min(blocks, key=lambda b: b[1])
        last_block  = max(blocks, key=lambda b: b[3])

        # Add random texts
        page.insert_text((page.rect.x0 + 12, first_block[1] - 5),
                         f"Random Top Text: {random.randint(1000,9999)}",
                         fontsize=12, fontname="helv", fill=(0,0,0))

        page.insert_text((page.rect.x0 + 12, last_block[3] + 15),
                         f"Random Bottom Text: {random.randint(1000,9999)}",
                         fontsize=12, fontname="helv", fill=(0,0,0))

        # Crop
        crop_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_block[3] + 20)
        page.set_cropbox(crop_rect)
    t2 = time.perf_counter()
    return doc, (t2 - t1)  # return doc + processing time

# ------------- MAIN SCRIPT ----------------
overall_start = time.perf_counter()
process = psutil.Process(os.getpid())

merged_pdf = fitz.open()
download_time = 0.0

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_and_process, i, pdf_url) for i in range(NUM_PDFS)]

    for future in as_completed(futures):
        doc, proc_time = future.result()
        merged_pdf.insert_pdf(doc)
        doc.close()
        download_time += proc_time

# Save merged result
merged_pdf.save(output_pdf, deflate=True)
merged_pdf.close()

overall_end = time.perf_counter()
total_time = overall_end - overall_start

# Memory usage stats
mem_info = process.memory_info()
rss_mb = mem_info.rss / (1024*1024)   # Resident memory in MB
vms_mb = mem_info.vms / (1024*1024)   # Virtual memory in MB

# Print results
# print(f"⏬ Total processing time (all workers): {download_time:.2f} seconds")
# print(f"⏱ Overall total time: {total_time:.2f} seconds")
# print(f"➡️ Average time per PDF: {total_time/NUM_PDFS:.2f} seconds")
# print(f"💾 Memory Usage -> RSS: {rss_mb:.2f} MB | VMS: {vms_mb:.2f} MB")


"""
📦 1. Storage Requirement

Avg size ≈ 35 KB per PDF.

For 1000 PDFs → 1000 × 35 KB = 35,000 KB ≈ 34 MB.

Merged PDF size will be similar (maybe +10–15% due to extra text/metadata).

Disk space needed: <100 MB (safe margin).

🧠 2. RAM Requirement

PyMuPDF (fitz) loads each PDF into memory temporarily.

A 50 KB PDF → typically expands 3–10× in memory (due to decompression, rendering, structures).

So ~0.2–0.5 MB per PDF in memory.

With 1000 PDFs, worst-case memory usage:
1000 × 0.5 MB ≈ 500 MB.

🔹 But since you process + merge sequentially in the thread loop (not storing all at once), peak RAM use is far less (~150 MB) (your test already showed ~112 MB).

⚡ 3. CPU Requirement

Each PDF → adds text + crops → very light CPU work (<5 ms).

For 1000 PDFs → total CPU work ~a few seconds, negligible compared to download time.

Even a dual-core CPU can handle it.

🌐 4. Network Requirement

Avg PDF size = 35 KB.

1000 PDFs = ~34 MB download total.

If your internet is:

10 Mbps (~1.25 MB/s) → ~30 sec.

50 Mbps (~6.25 MB/s) → ~6 sec.

100 Mbps (~12.5 MB/s) → ~3 sec.

👉 Network is the bottleneck, not CPU/RAM.

✅ Computational Requirement Summary (for 1000 PDFs, 20–50 KB each)

CPU: Dual-core is fine, Quad-core is better if you increase workers.

RAM: ~200 MB peak (so any system with ≥2 GB RAM is more than enough).

Disk: ~100 MB free.

Network: Needs to handle ~34 MB transfer (speed determines total time).
"""
