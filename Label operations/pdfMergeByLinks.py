from pypdf import PdfWriter
import requests
from io import BytesIO
import time

start_time = time.time()

pdf_urls = [
    "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434845647.pdf?request-content-type=application/force-download",

    "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434846094.pdf?request-content-type=application/force-download",

    "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/599/434848989.pdf?request-content-type=application/force-download",

    "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/389/434849072.pdf?request-content-type=application/force-download",

    "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/434853612.pdf?request-content-type=application/force-download",

    "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/434861925.pdf?request-content-type=application/force-download"
]

merger = PdfWriter()

for url in pdf_urls:
    response = requests.get(url)
    response.raise_for_status()

    pdf_file = BytesIO(response.content)
    merger.append(pdf_file)

# output_filename = "merged_using_urls.pdf"
merger.write("merged_using_urls.pdf")
merger.close()

print(f"Execution time: {time.time() - start_time:.4f} seconds")