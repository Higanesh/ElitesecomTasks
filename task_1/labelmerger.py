from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import io
from pypdf import PdfWriter
import datetime as dt
import psutil
import os
import time

# Variables to track peak memory usage and timing information
peak_memory = 0  # Peak memory usage in MB
peak_stage = ""  # Stage at which peak memory was recorded
last_time = time.time()  # Timestamp of last recorded stage time
longest_stage_time = 0  # Longest elapsed time between stages
longest_stage_name = ""  # Name of the stage with longest elapsed time

def log_memory_and_time(stage):
    """
    Logs the current memory usage and the time elapsed since the last call,
    updating the peak memory usage and longest stage duration trackers.
    """
    global peak_memory, peak_stage, last_time, longest_stage_time, longest_stage_name

    # Get current process memory usage in MB
    process = psutil.Process(os.getpid())
    mem_info_mb = process.memory_info().rss / (1024 * 1024)  # rss is Resident Set Size (physical memory)

    # Update peak memory and corresponding stage if current usage is higher
    if mem_info_mb > peak_memory:
        peak_memory = mem_info_mb
        peak_stage = stage

    # Calculate time elapsed since last stage
    current_time = time.time()
    elapsed = current_time - last_time
    last_time = current_time

    # Update longest stage time and name if current elapsed is greater
    if elapsed > longest_stage_time:
        longest_stage_time = elapsed
        longest_stage_name = stage

    # Print current memory and elapsed time for this stage
    print(f"💾 Memory at {stage}: {mem_info_mb:.2f} MB | ⏱ Stage time: {elapsed:.2f}s")

def print_summary():
    """Print summary of peak memory usage and longest stage duration."""
    print(f"\n📊 Peak memory usage: {peak_memory:.2f} MB at stage '{peak_stage}'")
    print(f"⏳ Longest stage: {longest_stage_name} ({longest_stage_time:.2f}s)")

# Read PDF URLs from file into a list, stripping any whitespace
with open("lebel_urls.txt") as f:
    pdf_urls = [line.strip() for line in f]

def download_pdf(url):
    """
    Downloads PDF content from the given URL.
    Returns a tuple of (url, content bytes) or (url, None) if download fails.
    """
    try:
        response = requests.get(url, timeout=10)  # Timeout after 10 seconds
        response.raise_for_status()  # Raise exception for HTTP errors
        return url, response.content
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return url, None

def merge_pdfs(urls):
    """
    Main function to download PDFs from URLs in parallel,
    merge them in the original order, and save the result to disk.
    Tracks and logs memory usage and timing at each stage.
    """
    start_time = dt.datetime.now()
    log_memory_and_time("start")  # Log memory/time at start
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Remove duplicate URLs to avoid redundant downloads
    unique_urls = list(set(urls))
    pdf_cache = {}

    # Download PDFs in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(download_pdf, url): url for url in unique_urls}
        # As each future completes, store successful downloads in pdf_cache
        for future in as_completed(futures):
            url, pdf_bytes = future.result()
            if pdf_bytes:
                pdf_cache[url] = pdf_bytes

    log_memory_and_time("after download")  # Log memory/time after downloads complete

    # Step 2: Merge PDFs in the original order from the initial URLs list
    # Using PdfWriter to append PDFs from the cached bytes
    merger = PdfWriter()
    for url in urls:
        if url in pdf_cache:
            merger.append(io.BytesIO(pdf_cache[url]))  # Append PDF from memory stream

    log_memory_and_time("after merge")  # Log memory/time after merging PDFs

    # Step 3: Write the merged PDF to an output file
    with open("new_merge_pdf.pdf", "wb") as f:
        merger.write(f)
    merger.close()  # Close the PdfWriter to free resources

    log_memory_and_time("end")  # Final memory/time log after saving file

    end_time = dt.datetime.now()
    print(f"✅ Done: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱ Total time: {(end_time - start_time).total_seconds():.2f}s")
    print(f"📄 Output: new_merge_pdf.pdf | Merged {len(urls)} files.")
    print_summary()  # Print peak memory and longest stage summary

def main(event):
    # Main entry point to run the PDF merging process
    merge_pdfs(pdf_urls)
    return {
        "statusCode": 200,
        "body": f"Merged PDF saved at merge_output.pdf with {len(pdf_urls)} files."
    }

if __name__ == "__main__":
    main({})
