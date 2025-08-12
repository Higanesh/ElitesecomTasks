# import time
# from concurrent.futures import ThreadPoolExecutor

# pdf_urls = [f"http://example.com/pdf{i}.pdf" for i in range(1, 1001)]

# def download_pdf(url):
#     time.sleep(0.1)  # simulate download time
#     return b"%PDF-1.4 dummy pdf content"

# def merge_pdfs(pdf_contents):
#     time.sleep(0.001 * len(pdf_contents))  # simulate merge time
#     return b"%PDF-1.4 merged pdf content"

# start_time = time.time()

# with ThreadPoolExecutor(max_workers=50) as executor:
#     pdf_contents = list(executor.map(download_pdf, pdf_urls))

# merged_pdf = merge_pdfs(pdf_contents)

# end_time = time.time()
# print(f"Parallel merging took {end_time - start_time:.2f} seconds.")


dummy_pdf_urls = [f"http://example.com/test_pdf_{i}.pdf" for i in range(1, 1001)]

for i in range(1, 1001):
    print(f"http://example.com/test_pdf_{i}.pdf")

end_time = time.time()
print(f"Parallel merging took {end_time - start_time:.2f} seconds.")
