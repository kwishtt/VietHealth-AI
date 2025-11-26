import requests

URL = "https://supvn.net/blogs/kien-thuc/bang-calories-theo-thuc-an-viet-nam"
OUTPUT_HTML = "page_source.html"

def save_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(URL, headers=headers)
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved HTML")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    save_html()
