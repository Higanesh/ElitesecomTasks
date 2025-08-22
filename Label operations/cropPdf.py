from pypdf import PdfReader,PdfWriter

reader = PdfReader("sample.pdf")
writer = PdfWriter()

crop_x1, crop_y1 = 0, 0
crop_x2, crop_y2 = 500, 450

for page in reader.pages:
    page.mediabox.lower_left = (crop_x1, crop_y1)
    page.mediabox.upper_right = (crop_x2, crop_y2)
    writer.add_page(page)

# Save cropped PDF
with open("cropped_Lower.pdf", "wb") as f:
    writer.write(f)