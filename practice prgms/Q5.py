import sys
import urllib.request
import re

def strip_html_tags(html):
    # Remove script/style sections
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)
    # Remove all HTML tags
    html = re.sub(r"<[^>]+>", "", html)
    # Replace multiple spaces/newlines with a single space
    html = re.sub(r"\s+", " ", html)
    return html.strip()

def main():
    if len(sys.argv) != 2:
        print("Provide URL")
        sys.exit(1)

    url = sys.argv[1]

    try:
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print("Error fetching URL:", e)
        sys.exit(1)

   
    clean_text = strip_html_tags(html)
    print(clean_text)

if __name__ == "__main__":
    main()
