from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
import io
from pypdf import PdfWriter
import datetime as dt
import psutil
import os
import time

peak_memory = 0  # MB
peak_stage = ""
last_time = time.time()
longest_stage_time = 0
longest_stage_name = ""

def log_memory_and_time(stage):
    global peak_memory, peak_stage, last_time, longest_stage_time, longest_stage_name

    # Memory usage
    process = psutil.Process(os.getpid())
    mem_info_mb = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB

    # Update peak memory
    if mem_info_mb > peak_memory:
        peak_memory = mem_info_mb
        peak_stage = stage

    # Time taken since last stage
    current_time = time.time()
    elapsed = current_time - last_time
    last_time = current_time

    # Update longest stage
    if elapsed > longest_stage_time:
        longest_stage_time = elapsed
        longest_stage_name = stage

    print(f"💾 Memory at {stage}: {mem_info_mb:.2f} MB | ⏱ Stage time: {elapsed:.2f}s")

def print_summary():
    print(f"\n📊 Peak memory usage: {peak_memory:.2f} MB at stage '{peak_stage}'")
    print(f"⏳ Longest stage: {longest_stage_name} ({longest_stage_time:.2f}s)")


with open("lebel_urls.txt") as f:
    pdf_urls = [line.strip() for line in f]

def download_pdf(url):
    """Download a PDF from a URL and return its bytes."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises an error if the HTTP status is not OK
        return url,response.content
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return url,None

def merge_pdfs(urls):
    start_time = dt.datetime.now()
    log_memory_and_time("start")
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Download unique PDFs in parallel
    unique_urls = list(set(urls))
    pdf_cache = {}

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(download_pdf, url): url for url in unique_urls}
        for future in as_completed(futures):
            url, pdf_bytes = future.result()
            if pdf_bytes:
                pdf_cache[url] = pdf_bytes

    log_memory_and_time("after download")
    # Step 2: Merge directly in original order (minimizes RAM use)
    merger = PdfWriter()
    for url in urls:
        if url in pdf_cache:
            merger.append(io.BytesIO(pdf_cache[url]))

    log_memory_and_time("after merge")
    # Step 3: Save merged PDF
    with open("new_merge_pdf.pdf", "wb") as f:
        merger.write(f)
    merger.close()

    log_memory_and_time("end")

    end_time = dt.datetime.now()
    print(f"✅ Done: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱ Total time: {(end_time - start_time).total_seconds():.2f}s")
    print(f"📄 Output: new_merge_pdf.pdf | Merged {len(urls)} files.")
    print_summary()

def main(event):
    merge_pdfs(pdf_urls)
    return {
        "statusCode": 200,
        "body": f"Merged PDF saved at merge_output.pdf with {len(pdf_urls)} files."
    }

if __name__ == "__main__":
    main({})


