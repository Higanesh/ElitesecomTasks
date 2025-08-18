#merge that all 100 pdfs

import fitz
import random
import io
import requests
import time  # <-- import time module

start_time = time.perf_counter()  # Start timer

for i in range(100):
    pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"

    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to download {pdf_url}")

    pdf_bytes = io.BytesIO(response.content)
    doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")

    output_pdf = rf"D:\myProjects\ElitesecomTasks\Output PDFs\100_pdfs\cropped_with_text_{i}.pdf"

    page = doc[0]
    blocks = page.get_text("blocks")
    if not blocks:
        raise Exception("❌ No text found in PDF.")

    first_block = min(blocks, key=lambda b: b[1])
    last_block = max(blocks, key=lambda b: b[3])

    # Top text
    random_top_text = "Random Top Text: " + str(random.randint(1000, 9999))
    page.insert_text(
        (page.rect.x0 + 12, first_block[1] - 5),
        random_top_text,
        fontsize=12,
        fontname="helv",
        fill=(0, 0, 0)
    )

    # Bottom text
    random_bottom_text = "Random Bottom Text: " + str(random.randint(1000, 9999))
    page.insert_text(
        (page.rect.x0 + 12, last_block[3] + 15),
        random_bottom_text,
        fontsize=12,
        fontname="helv",
        fill=(0, 0, 0)
    )

    # Crop bottom blank space
    blocks_after = page.get_text("blocks")
    last_y_after = max(b[3] for b in blocks_after)
    crop_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_y_after + 5)
    page.set_cropbox(crop_rect)

    doc.save(output_pdf)

end_time = time.perf_counter()  # End timer

total_time = end_time - start_time
print(f"⏱ Total time to process 100 PDFs: {total_time:.2f} seconds")
print(f"⏱ Average time per PDF: {total_time/100:.2f} seconds")
