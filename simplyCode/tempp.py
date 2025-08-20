import fitz
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import sys
import time
import psutil, os

pdf_urls = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"
output_pdf = "cropped_output_self_100.pdf"

# ----------------------------
# Custom Exception
# ----------------------------
class PDFCropError(Exception):
    pass

def download_and_crop_pdf(i, url):
    try:
        response = requests.get(url, timeout=15)  # add timeout for safety
        response.raise_for_status()  # raises HTTPError for bad status codes
    except Exception as e:
        print(f"Failed to download PDF Internet Issue: {e}", file=sys.stderr)
        return None

    try:
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
    except Exception as e:
        raise PDFCropError(f"Failed to open PDF: {e}")

    page = doc[0]  # Get the first page
    blocks = page.get_text("blocks")
    if not blocks:
        raise PDFCropError("No text blocks found in the PDF.")
    
    try:
        first_block = min(blocks, key=lambda b: b[1])
        last_block  = max(blocks, key=lambda b: b[3])

        page.insert_text((page.rect.x0 + 12, first_block[1] - 5),
                        f"Random Top Text: {random.randint(1000,9999)}",
                        fontsize=12, fontname="helv", fill=(0,0,0))
        
        page.insert_text((page.rect.x0 + 12, last_block[3] + 15),
                        f"Random Bottom Text: {random.randint(1000,9999)}",
                        fontsize=12, fontname="helv", fill=(0,0,0))
    except Exception as e:
        raise PDFCropError(f"Failed to insert text in PDF: {e}")

    try:
        new_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_block[3] + 20)
        page.set_cropbox(new_rect)
    except Exception as e:
        raise PDFCropError(f"Failed to crop PDF: {e}")

    return doc


# ----------------------------
# Benchmark Runner
# ----------------------------
def run_benchmark(core_limit):
    # Restrict CPU cores
    p = psutil.Process(os.getpid())
    p.cpu_affinity(list(range(core_limit)))

    start = time.perf_counter()

    merged_pdf = fitz.open()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_and_crop_pdf, i, pdf_urls) for i in range(100)]

        for future in as_completed(futures):
            doc = future.result()
            if doc:  # only merge if valid
                merged_pdf.insert_pdf(doc)
                doc.close()
        
    merged_pdf.save(f"output_{core_limit}_cores.pdf")
    merged_pdf.close()

    end = time.perf_counter()
    print(f"Cores: {core_limit}, Time: {end - start:.2f} sec")


# ----------------------------
# Run Benchmarks with 1, 2, 4 cores
# ----------------------------
for cores in [1, 2, 4]:
    run_benchmark(cores)
