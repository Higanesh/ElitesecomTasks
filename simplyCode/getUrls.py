import json

input_file = r"D:\myProjects\ElitesecomTasks\Input files\200rawdata.txt"
output_file = r"D:\myProjects\ElitesecomTasks\Input files\200label_urls.txt"

label_urls = []

# Read each line (dictionary) and extract label_url
with open(input_file, "r") as f:
    for line in f:
        line = line.strip()
        if line:  # skip empty lines
            try:
                data = json.loads(line)  # parse dictionary
                label_urls.append(data["label_url"])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️ Skipping line due to error: {e}")

# Write all label URLs to output file
with open(output_file, "w") as f:
    for url in label_urls:
        f.write(url + "\n")

print(f"✅ Extracted {len(label_urls)} label URLs and saved to {output_file}")
