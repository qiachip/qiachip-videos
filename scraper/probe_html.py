import requests
from bs4 import BeautifulSoup
import re
import os

def main():
    url = "https://qiachip.github.io/qiachip/KR0548-1CH/QIACHIP_KR0548-1CH/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"--- Probing HTML Structure: {url} ---")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding

        # 1. HTTP status_code
        print(f"1. HTTP Status Code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. <title> 标签内容
        title_tag = soup.find('title')
        print(f"2. <title>: {title_tag.get_text(strip=True) if title_tag else 'None'}")

        # 3. 所有 <h1> 标签内容
        h1_tags = soup.find_all('h1')
        print("3. All <h1> tags:")
        for h1 in h1_tags:
            print(f"   - {h1.get_text(strip=True)}")

        # 4. 所有 <h2> 标签内容（最多前5个）
        h2_tags = soup.find_all('h2')[:5]
        print("4. All <h2> tags (up to 5):")
        for h2 in h2_tags:
            print(f"   - {h2.get_text(strip=True)}")

        # 5. <meta name="description"> 的 content 属性
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        print(f"5. Meta Description: {meta_desc.get('content', 'None') if meta_desc else 'None'}")

        # 6. 文本中包含 "KR0548" 的所有片段（关键词前后各取80字符）
        text_content = soup.get_text()
        matches = list(re.finditer(r"KR0548", text_content))
        print(f"6. Snippets for 'KR0548' ({len(matches)} found):")
        for i, match in enumerate(matches):
            start = max(0, match.start() - 80)
            end = min(len(text_content), match.end() + 80)
            snippet = text_content[start:end].replace('\n', ' ').strip()
            print(f"   Snippet {i+1}: ...{snippet}...")

        # 完整 HTML 保存到 data/raw/debug_html.html
        os.makedirs("data/raw", exist_ok=True)
        with open("data/raw/debug_html.html", "w", encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n--- Full HTML saved to data/raw/debug_html.html ---")

    except Exception as e:
        print(f"Error during probe_html: {e}")

if __name__ == "__main__":
    main()
