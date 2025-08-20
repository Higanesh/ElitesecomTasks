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

class PDFCropError(Exception):
    """Raised when cropping PDF fails"""
    pass

# -------------------------------
# ✅ Download, Crop & Insert Text
# -------------------------------
def download_and_crop_pdf(url, mode="auto"):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise PDFDownloadError(f"Failed to download PDF: {e}")

    try:
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
    except Exception as e:
        raise PDFOpenError(f"Failed to open PDF: {e}")

    page = doc[0]

    try:
        if mode == "auto":
            blocks = page.get_text("blocks")
            if not blocks:
                raise PDFTextBlockError("No text blocks found in the PDF.")

            first_block = min(blocks, key=lambda b: b[1])
            last_block = max(blocks, key=lambda b: b[3])

            # Insert random text
            page.insert_text((page.rect.x0 + 12, max(first_block[1] - 5, page.rect.y0 + 5)),
                             f"Random Top Text: {random.randint(1000,9999)}",
                             fontsize=12, fontname="helv", fill=(0,0,0))
            page.insert_text((page.rect.x0 + 12, min(last_block[3] + 15, page.rect.y1 - 15)),
                             f"Random Bottom Text: {random.randint(1000,9999)}",
                             fontsize=12, fontname="helv", fill=(0,0,0))

            # Crop page safely
            bottom_limit = min(last_block[3] + 20, page.rect.y1)
            new_rect = fitz.Rect(page.rect.x0 + 5, page.rect.y0, page.rect.x1 - 5, bottom_limit)
            if new_rect.is_empty or new_rect.height < 20:
                new_rect = page.rect
            page.set_cropbox(new_rect)

        elif mode in ["top", "bottom"]:
            height = page.rect.height
            width = page.rect.width
            mid = height / 2
            margin = 5
            new_rect = (fitz.Rect(0, 0, width, mid - margin) if mode == "top"
                        else fitz.Rect(0, mid + margin, width, height))
            page.set_cropbox(new_rect)

        else:
            raise ValueError("Invalid mode. Use 'auto', 'top', or 'bottom'.")

    except Exception as e:
        raise PDFCropError(f"Failed during cropping or text insertion ({mode}): {e}")

    return doc

# -------------------------------
# ✅ Main Execution
# -------------------------------
def main():
    # Input PDF URLs
    with open(r"D:\myProjects\ElitesecomTasks\Input files\200label_urls.txt") as f:
        pdf_urls = [line.strip() for line in f]

    output_pdf = "cropped_merged_output.pdf"
    merged_pdf = fitz.open()

    start_time = time.perf_counter()

    # Use ThreadPoolExecutor for parallel downloads
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(download_and_crop_pdf, url, "auto"): url for url in pdf_urls}

        for future in as_completed(futures):
            url = futures[future]
            try:
                doc = future.result()
                if doc:
                    merged_pdf.insert_pdf(doc)
                    doc.close()
                    print(f"✅ Processed: {url}")
            except (PDFDownloadError, PDFOpenError, PDFTextBlockError, PDFCropError, ValueError) as e:
                print(f"⚠️ Skipped {url} - {e}")

    # Save merged PDF
    merged_pdf.save(output_pdf)
    merged_pdf.close()

    end_time = time.perf_counter()
    print(f"\n✅ Finished in {end_time - start_time:.2f} seconds")
    print(f"✅ Output saved as: {output_pdf}")

# -------------------------------
if __name__ == "__main__":
    main()
