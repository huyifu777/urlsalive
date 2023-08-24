import requests
import csv
import sys
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os
import pyfiglet

banner_text = "urlsalive"
style = "slant"  # Specify the desired font style
# Set the version number and author
version = "1.0"
author = "huyifu777\nhttps://github.com/huyifu777/urlsalive"

# Generate the banner
banner = pyfiglet.figlet_format(banner_text, font=style)

# Add the version number and author as a subscript
subscript = f"Version: {version}\nAuthor: {author}"

# Combine the banner and subscript
final_text = f"{banner}\n{subscript}"

# Print the final text
print(final_text)

def check_url(url, method="GET"):
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url)
        else:
            print(f"Invalid HTTP method: {method}")
            return

        status_code = response.status_code
        response_size = len(response.content)

        return status_code, response_size, url
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while checking {url}: {e}")
        return None, None, url

# ...

def batch_check_urls_from_file(file_path, method="GET"):
    try:
        with open(file_path, "r") as file:
            urls = file.readlines()
            urls = [url.strip() for url in urls]

        results = []
        total_urls = len(urls)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_url, url, method) for url in urls]

            for future in tqdm(futures, total=total_urls, desc="Checking URLs"):
                status_code, response_size, url = future.result()
                results.append((method, status_code, response_size, url))

        return results
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error occurred while reading file: {e}")
        return []

def write_results_to_csv(results, output_file):
    fieldnames = ["Method", "Status Code", "Response Size", "URL"]

    # 检查输出文件是否已存在
    file_exists = os.path.exists(output_file)

    # 读取现有内容（如果文件已存在）
    existing_content = []
    if file_exists:
        with open(output_file, "r") as file:
            reader = csv.reader(file)
            existing_content = list(reader)

    # 将新结果与现有内容合并
    merged_content = existing_content + [fieldnames] + results

    # 将合并后的内容写回文件
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(merged_content)

# Get the file path and output file name from command line arguments
if len(sys.argv) < 3:
    print("Please provide the file path and output file name as command line arguments.")
    sys.exit(1)

file_path = sys.argv[1]
output_file = sys.argv[2]

# Execute batch checks using GET method and write results to CSV
get_results = batch_check_urls_from_file(file_path)
write_results_to_csv(get_results, output_file)

# Execute batch checks using POST method and append results to CSV
post_results = batch_check_urls_from_file(file_path, method="POST")
write_results_to_csv(post_results, output_file)