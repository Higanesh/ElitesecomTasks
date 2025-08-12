from pypdf import PdfReader

# Path to your merged PDF
pdf_path = "mergeAll.pdf"

# Open and read the PDF
reader = PdfReader(pdf_path)

# Loop through pages and print text
for page_num, page in enumerate(reader.pages, start=1):
    text = page.extract_text()
    print(f"\n--- Page {page_num} ---\n")
    print(text if text else "[No text found on this page]")

page_no = int(input("Enter Page Number: "))

