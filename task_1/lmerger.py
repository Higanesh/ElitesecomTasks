import requests
import io
from pypdf import PdfWriter
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed

# Example URLs (can be dynamic)
# PDF_URLS = [
#     "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434845647.pdf?request-content-type=application/force-download",
#     "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434846094.pdf?request-content-type=application/force-download",
#     "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434848989.pdf?request-content-type=application/force-download"
#  ] * 500   # simulate duplicates

# PDF_URLS = [f"https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434845647.pdf?request-content-type=application/force-download"
#             for _ in range(1000)]  

with open("gutenberg_1000_pdfs.txt") as f:
    PDF_URLS = [line.strip() for line in f]


def download_pdf(url):
    """Download a PDF, return (url, content_bytes) or (url, None) if failed."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return url, response.content
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return url, None

def merge_pdfs(urls, output_path):
    start_time = dt.datetime.now()
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Download unique PDFs in parallel
    unique_urls = list(set(urls))
    pdf_cache = {}

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(download_pdf, url): url for url in unique_urls}
        for future in as_completed(futures):
            url, pdf_bytes = future.result()
            if pdf_bytes:
                pdf_cache[url] = pdf_bytes

    # Step 2: Merge directly in original order (minimizes RAM use)
    merger = PdfWriter()
    for url in urls:
        if url in pdf_cache:
            merger.append(io.BytesIO(pdf_cache[url]))

    # Step 3: Save merged PDF
    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()

    end_time = dt.datetime.now()
    print(f"✅ Done: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱ Total time: {(end_time - start_time).total_seconds():.2f}s")
    print(f"📄 Output: {output_path} | Merged {len(urls)} files.")

# Lambda handler
def lambda_handler(event, context):
    output_path = "/tmp/merged_output.pdf" if context else "./merged_output.pdf"
    merge_pdfs(PDF_URLS, output_path)
    return {
        "statusCode": 200,
        "body": f"Merged PDF saved at {output_path} with {len(PDF_URLS)} files."
    }

# Local testing
if __name__ == "__main__":
    lambda_handler({}, None)