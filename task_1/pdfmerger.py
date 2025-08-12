from pypdf import PdfWriter
import os

# pdf merger object
merger = PdfWriter()

# Folder containing PDFs
folder_path = "."

# Loop through all PDF files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):  # Only PDF files
        file_path = os.path.join(folder_path, filename)
        merger.append(file_path)


# # Append files for merge
# merger.append("sample.pdf")

# merger.append("test.pdf")

# merger.append("cropped_Upper.pdf")

# merger.append("cropped_Lower.pdf")

# Write the merged PDF to a new file
merger.write("mergeAll.pdf")

merger.close()