import requests

API_URL = "https://gutendex.com/books"
pdf_list = []
page = 1

while len(pdf_list) < 1000:
    resp = requests.get(API_URL, params={"page": page})
    resp.raise_for_status()
    data = resp.json()

    for book in data["results"]:
        formats = book["formats"]
        # Get only direct PDF links (not zipped unless you want them)
        for fmt, url in formats.items():
            if "application/pdf" in fmt and url.endswith(".pdf"):
                pdf_list.append(url)
                break  # take first matching PDF
        if len(pdf_list) >= 1000:
            break

    page += 1
    if not data["next"]:
        break

# Save working URLs to file
with open("gutenberg_1000_pdfs.txt", "w") as f:
    for url in pdf_list:
        f.write(url + "\n")

print(f"Collected {len(pdf_list)} working PDF URLs.")
