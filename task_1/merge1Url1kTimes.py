import time
from concurrent.futures import ThreadPoolExecutor
import requests
import io
from pypdf import PdfWriter

# i have 1 pdf url so that i repeat that same url 1000 times
pdf_urls = [f"https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434845647.pdf?request-content-type=application/force-download"
            for _ in range(1000)]  

def download_pdf(url):
    try:
        # time.sleep(0.1)  # simulate download time
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises an error if the HTTP status is not OK
        return response.content
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def merge_pdfs(pdf_contents):
    time.sleep(0.001 * len(pdf_contents))  # simulate merge time
    merger = PdfWriter() # Creates a new PDF writer to build the merged PDF.
    for pdf_bytes in pdf_contents: # Iterates over each downloaded PDF’s bytes.
        if pdf_bytes:  # skip None
            merger.append(io.BytesIO(pdf_bytes)) # Wraps bytes in a BytesIO stream and appends it to the writer.
    output = io.BytesIO() # Creates an in-memory output buffer for the merged file.
    merger.write(output)
    merger.close()
    return output.getvalue() # Returns the merged PDF as bytes.


start_time = time.time() # Records start timestamp.

with ThreadPoolExecutor(max_workers=50) as executor: # Creates a thread pool with up to 50 threads for concurrent downloading.

    pdf_contents = list(executor.map(download_pdf, pdf_urls)) # Submits all URLs to the pool and collects their byte contents as a list (order preserved).

merged_pdf = merge_pdfs(pdf_contents) # Merges all downloaded PDFs into one byte string.

# Save merged file
with open("merged_output.pdf", "wb") as f:
    f.write(merged_pdf)

end_time = time.time() # Records end timestamp.
print(f"Parallel merging took {end_time - start_time:.2f} seconds.")   