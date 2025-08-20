import fitz
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import time

# -------------------------------
# ✅ Custom Exception Classes
# -------------------------------
class PDFDownloadError(Exception):
    """Raised when downloading the PDF fails"""
    pass

class PDFOpenError(Exception):
    """Raised when opening the PDF fails"""
    pass

class PDFTextBlockError(Exception):
    """Raised when no text blocks are found in PDF"""
    pass

class PDFInsertTextError(Exception):
    """Raised when inserting text into PDF fails"""
    pass

class PDFCropError(Exception):
    """Raised when cropping PDF fails"""
    pass

# -------------------------------
# ✅ Function to Download & Crop
# -------------------------------
def download_and_crop_pdf(i, url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise PDFDownloadError(f"Failed to download PDF: {e}")

    try:
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
    except Exception as e:
        raise PDFOpenError(f"Failed to open PDF: {e}")

    try:
        page = doc[0]
        blocks = page.get_text("blocks")
    except Exception as e:
        raise PDFTextBlockError("No text blocks found in the PDF.")

    try:
        first_block = min(blocks, key=lambda b: b[1])
        last_block  = max(blocks, key=lambda b: b[3])

        page.insert_text((page.rect.x0 + 12, first_block[1] - 5),
                        f"Random Top Text: {random.randint(1000,9999)}",
                        fontsize=12, fontname="helv", fill=(0,0,0))

        page.insert_text((page.rect.x0 + 12, last_block[3] + 15),
                        f"Random Bottom Text: {random.randint(1000,9999)}",
                        fontsize=12, fontname="helv", fill=(0,0,0))
    except requests.exceptions.RequestException as e:
        raise PDFInsertTextError(f"Failed to insert text: {e}")

    try:
        new_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_block[3] + 20)
        page.set_cropbox(new_rect)
    except Exception as e:
        raise PDFCropError(f"Failed to crop PDF: {e}")

    return doc


# -------------------------------
# ✅ Main Execution with Timer
# -------------------------------
with open(r"D:\myProjects\ElitesecomTasks\Input files\200label_urls.txt") as f:
        pdf_urls = [line.strip() for line in f]
output_pdf = "cropped_output_self_200.pdf"
merged_pdf = fitz.open()

start_time = time.perf_counter()  # start timer

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_and_crop_pdf, url)]

    for future in as_completed(futures):
        try:
            doc = future.result()
            if doc:
                merged_pdf.insert_pdf(doc)
                doc.close()
        except (PDFDownloadError, PDFOpenError, PDFTextBlockError,
                PDFInsertTextError, PDFCropError) as e:
            print(f"⚠️ Error: {e}")

# Save the merged PDF
merged_pdf.save(output_pdf)
merged_pdf.close()

end_time = time.perf_counter()  # end timer
print(f"\n✅ Execution finished in {end_time - start_time:.2f} seconds")
print(f"✅ Output saved as: {output_pdf}")
