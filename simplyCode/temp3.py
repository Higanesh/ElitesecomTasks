import fitz
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import time
import psutil   # for CPU, RAM, disk info
import subprocess, re
  # for network speed test

# -------------------------------
# ✅ Custom Exception Classes
# -------------------------------
class PDFDownloadError(Exception): pass
class PDFOpenError(Exception): pass
class PDFTextBlockError(Exception): pass
class PDFInsertTextError(Exception): pass
class PDFCropError(Exception): pass


# -------------------------------
# ✅ Detect System Resources
# -------------------------------
def detect_system_resources():
    try:
        cpu_cores = psutil.cpu_count(logical=True)
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        disk_gb = round(psutil.disk_usage('/').total / (1024**3), 2)

        print("\n🔍 Detecting system resources...")
        print(f"🖥️ CPU Cores: {cpu_cores}")
        print(f"💾 RAM: {ram_gb} GB")
        print(f"📀 Disk: {disk_gb} GB")

        # Measure network speed (download only)
        print("🌐 Testing network speed... (this may take a few seconds)")
        
        try:
            result = subprocess.run(["fast"], capture_output=True, text=True, timeout=30)
            match = re.search(r"Download:\s*([\d.]+)\s*Mbps", result.stdout)
            download_speed = float(match.group(1)) if match else None
        except Exception as e:
            print("⚠️ Network speed test failed:", e)
            download_speed = None  # fallback

        # If speed not detected, assume 10 Mbps as safe default
        if not download_speed:
            download_speed = 10.0
            print("⚠️ Using fallback network speed: 10 Mbps")

        return cpu_cores, ram_gb, disk_gb, download_speed

    except Exception as e:
        print("❌ Error detecting system resources:", e)
        # Return safe defaults
        return 1, 4, 100, 10.0

# -------------------------------
# ✅ Predict Runtime
# -------------------------------
def predict_runtime(pdf_size_mb, pdf_count, cpu_cores, ram_gb, download_speed):
    # download time
    total_download_time = (pdf_size_mb * pdf_count) / (download_speed / 8)  # sec

    # cpu time (assume ~0.1s per PDF sequential)
    sequential_cpu_time = pdf_count * 0.1
    cpu_time = sequential_cpu_time / min(cpu_cores, pdf_count)

    # add small disk overhead
    disk_time = 0.5

    total_estimated_time = total_download_time + cpu_time + disk_time

    print("\n📊 Predicted Runtime:")
    print(f" - Download time: {total_download_time:.2f} sec")
    print(f" - CPU processing: {cpu_time:.2f} sec")
    print(f" - Disk overhead: {disk_time:.2f} sec")
    print(f"✅ Total Estimate: {total_estimated_time:.2f} sec\n")

    return total_estimated_time


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
    except Exception:
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
    except Exception as e:
        raise PDFInsertTextError(f"Failed to insert text: {e}")

    try:
        new_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_block[3] + 20)
        page.set_cropbox(new_rect)
    except Exception as e:
        raise PDFCropError(f"Failed to crop PDF: {e}")

    return doc


# -------------------------------
# ✅ Main Execution
# -------------------------------
if __name__ == "__main__":
    pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"
    output_pdf = "cropped_output_self_100.pdf"
    merged_pdf = fitz.open()

    # Step 1: Detect resources
    cores, ram, disk, net_speed = detect_system_resources()

    # Step 2: Predict runtime (assume PDF size ~0.05 MB, 50 files)
    predict_runtime(pdf_size_mb=0.05, pdf_count=50,
                    cpu_cores=cores, ram_gb=ram, download_speed=net_speed)

    # Step 3: Run actual execution
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_and_crop_pdf, i, pdf_url) for i in range(50)]

        for future in as_completed(futures):
            try:
                doc = future.result()
                if doc:
                    merged_pdf.insert_pdf(doc)
                    doc.close()
            except (PDFDownloadError, PDFOpenError, PDFTextBlockError,
                    PDFInsertTextError, PDFCropError) as e:
                print(f"⚠️ Error: {e}")

    merged_pdf.save(output_pdf)
    merged_pdf.close()

    end_time = time.perf_counter()
    print(f"\n✅ Execution finished in {end_time - start_time:.2f} seconds")
    print(f"✅ Output saved as: {output_pdf}")
