import fitz  # PyMuPDF - for rendering PDF pages as images
import matplotlib.pyplot as plt  # For displaying PDF page and selecting coordinates
import numpy as np  # For handling image arrays
from pypdf import PdfReader, PdfWriter  # For cropping PDF pages
import requests  # For downloading PDF from a URL
import io  # For handling in-memory files

# -------------------------------------------------------
# Step 1: PDF URL (Change this to your desired PDF link)
# -------------------------------------------------------
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/434861925.pdf?request-content-type=application/force-download"

# -------------------------------------------------------
# Step 2: Download PDF from URL
# -------------------------------------------------------
response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download {pdf_url}")

# Store PDF in memory (so we don't have to save it to disk)
pdf_bytes = io.BytesIO(response.content)

# -------------------------------------------------------
# Step 3: Open PDF in two libraries
# -------------------------------------------------------
doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # For rendering page as image
reader = PdfReader(pdf_bytes)  # For cropping pages
writer = PdfWriter()  # For saving cropped result

# -------------------------------------------------------
# Step 4: Render the first page as an image
# -------------------------------------------------------
page = doc[0]  # First page
pix = page.get_pixmap()  # Convert PDF page to raster image

# Convert pixmap data to NumPy array for Matplotlib display
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

# -------------------------------------------------------
# Step 5: Display PDF page and allow user to click two points
# -------------------------------------------------------
fig, ax = plt.subplots()
# Show page image, with PDF coordinates mapped
ax.imshow(img, extent=(0, page.rect.width, 0, page.rect.height), origin="lower")

coords = []  # Will store two clicked points

def onclick(event):
    """Capture two click coordinates and close the plot."""
    if event.xdata is not None and event.ydata is not None:
        # Convert clicked Y coordinate to PDF coordinate system
        y_pdf = page.rect.height - event.ydata
        coords.append((event.xdata, y_pdf))
        print(f"Clicked at (PDF coords): ({event.xdata:.2f}, {y_pdf:.2f})")
        
        # If two points selected → close the plot
        if len(coords) == 2:
            print("Bottom-left:", coords[0], "Top-right:", coords[1])
            plt.close()

# Connect mouse click event
fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()

# -------------------------------------------------------
# Step 6: Crop the PDF based on selected coordinates
# -------------------------------------------------------
for page in reader.pages:
    page.mediabox.lower_left = (coords[0][0], coords[0][1])
    page.mediabox.upper_right = (coords[1][0], coords[1][1])
    writer.add_page(page)

# -------------------------------------------------------
# Step 7: Save cropped PDF to file
# -------------------------------------------------------
with open("cropped_label.pdf", "wb") as f:
    writer.write(f)

print("✅ Cropped PDF saved as 'cropped_label.pdf'")


"""Download the PDF from a URL.

Open it in both PyMuPDF (for rendering) and pypdf (for cropping).

Display the page so you can click two points.

Crop all pages to that rectangle.

Save the cropped version."""