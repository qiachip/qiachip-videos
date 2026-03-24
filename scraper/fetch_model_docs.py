import json
import requests
from bs4 import BeautifulSoup
import time
import os
import re

def extract_keywords(h1_text, model_name):
    """
    严格遵循规则提取关键词：
    1. 合并电压规格 (DC/AC + 空格 + 电压)
    2. 按空格分词
    3. 过滤无意义词、孤立 DC/AC、孤立电压值、过短词
    """
    # 第一步：合并电压规格
    # 例: "DC 7-48V" -> "DC7-48V", "AC 220V" -> "AC220V"
    merged_text = re.sub(r'(DC|AC)\s+(\d[\d\-\.]*V)', r'\1\2', h1_text, flags=re.IGNORECASE)

    # 第二步：按空格分词
    tokens = merged_text.split()

    # 第三步：过滤词列表
    stop_words = {
        "QIACHIP", "Instruction", "Manual", "User", "Guide",
        "How", "To", "Use", "The", "A", "An", "And", "Or",
        "For", "With", "Of", "In", "Is", "Are", "This", "That",
        "Smart", "Remote", "Control", "Wireless", "Module"
    }
    stop_words_lower = {w.lower() for w in stop_words}

    keywords = []
    seen = set()

    for token in tokens:
        t_lower = token.lower()

        # 1. 过滤完全无意义的词
        if t_lower in stop_words_lower:
            continue

        # 2. 过滤型号名称本身 (通常不需要出现在关键词中)
        if t_lower == model_name.lower():
            continue

        # 3. 过滤纯单词 "DC" 或 "AC" (孤立词)
        if token.upper() in ["DC", "AC"]:
            continue

        # 4. 过滤纯电压数字 (如 "7-48V", "12V" - 未合并成功的孤立电压)
        if re.match(r'^\d[\d\-\.]*V$', token, re.IGNORECASE):
            continue

        # 5. 过滤长度小于 2 的词
        if len(token) < 2:
            continue

        # 去重并保留
        if t_lower not in seen:
            keywords.append(token)
            seen.add(t_lower)

    return keywords

def main():
    input_file = "data/raw/model_list.json"
    output_file = "data/raw/model_docs.json"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    models = data.get("models", [])
    results = {}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Starting to fetch documentation for {len(models)} models...\n")

    for model in models:
        url = f"https://qiachip.github.io/qiachip/{model}/QIACHIP_{model}/"

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取第一个 h1
                h1_tag = soup.find('h1')
                h1_text = h1_tag.get_text(strip=True) if h1_tag else ""

                if h1_text:
                    keywords = extract_keywords(h1_text, model)
                    results[model] = {
                        "title": h1_text,
                        "keywords": keywords
                    }
                    print(f"[{model}] OK: {h1_text}")
                else:
                    print(f"[{model}] WARNING: No H1 found.")
                    results[model] = {"title": "", "keywords": []}
            else:
                print(f"[{model}] ERROR: HTTP {response.status_code}")
                results[model] = {"title": f"HTTP Error {response.status_code}", "keywords": []}

        except Exception as e:
            print(f"[{model}] EXCEPTION: {e}")
            results[model] = {"title": "Fetch Exception", "keywords": []}

        # 间隔 0.5 秒
        time.sleep(0.5)

    # 保存结果
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted! Results saved to {output_file}")

if __name__ == "__main__":
    main()
