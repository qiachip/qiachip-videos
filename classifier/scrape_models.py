#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import logging
import sys
from datetime import datetime

# 设置编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrape_models.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 定义型号前缀规则（与 extract_model.py 保持一致）
PREFIX_PATTERNS = {
    'KR': r'KR\d+[A-Z0-9]*(?:[-_][A-Z0-9]+)*',
    'KT': r'KT\d+[A-Z0-9]*(?:[-_][A-Z0-9]+)*',
    'RX': r'RX\d+[A-Z0-9]*(?:[-][A-Z0-9]+)*',
    'TX': r'TX\d+[A-Z0-9]*(?:[-][A-Z0-9]+)*',
    'QA': r'QA[-]?[A-Z0-9]+(?:[-][0-9]+)*',
    'DT': r'DT\d+[A-Z0-9]*',
    'ZB': r'ZB[A-Z]+[-]?\d+',
    'SM': r'SM[-]\d+[-][A-Z0-9]+',
    'KEY': r'KEY\d+'
}

# 明确排除的误匹配词（与 extract_model.py 保持一致）
EXCLUDED_WORDS = {
    'DC12V', 'DC24V', 'DC5V', 'DC6V', 'DC3V', 'DC48V', 'DC110V',
    'AC110V', 'AC220V', 'AC380V', 'AC12V', 'AC24V',
    '5V', '12V', '24V', '48V', '110V', '220V', '380V',
    'ON', 'OFF', 'DIY', 'RF', 'USB', 'GND', 'VCC', 'LED',
    'QIACHIP', 'WIFI', 'BLUETOOTH', 'BLUETOOTH',
    'HTTP', 'HTTPS', 'HTML', 'URL', 'API', 'JSON',
    'TEST', 'REVIEW', 'VIDEO', 'HOW', 'TO', 'WITH', 'FOR',
    'AND', 'THE', 'OF', 'IN', 'ON', 'AT', 'BY', 'FROM',
    'TO', 'FOR', 'WITH', 'BY', 'FROM', 'AS', 'IS', 'ARE',
    'BE', 'BEEN', 'HAVE', 'HAS', 'HAD', 'DO', 'DOES', 'DID',
    'WILL', 'WOULD', 'COULD', 'SHOULD', 'MAY', 'MIGHT', 'MUST'
}

def extract_models_from_text(text: str) -> set:
    """从文本中提取所有匹配的型号（使用严格的前缀规则）"""
    if not text:
        return set()

    matched_models = set()
    text_lower = text.lower()  # 用于排除词检查

    # 对每个前缀进行匹配
    for prefix, pattern in PREFIX_PATTERNS.items():
        # 使用正则查找所有匹配项
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            # 转换为大写（统一为大写格式）
            standardized_match = match.upper()

            # 检查是否在排除列表中
            if standardized_match not in EXCLUDED_WORDS:
                # 确保匹配的单词边界（避免部分匹配）
                if re.search(r'\b' + re.escape(standardized_match) + r'\b', text, re.IGNORECASE):
                    matched_models.add(standardized_match)

    return matched_models

def scrape_qiachip_models():
    """从 QIACHIP 官网抓取产品型号"""
    url = "https://qiachip.github.io/qiachip/"

    try:
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        logging.info(f"正在抓取 {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # 使用 BeautifulSoup 解析页面
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有可能的型号
        models = set()

        # 1. 查找表格中的型号
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                # 检查每一列
                for cell in row.find_all(['td', 'th']):
                    text = cell.get_text(strip=True)
                    cell_models = extract_models_from_text(text)
                    models.update(cell_models)

        # 2. 查找链接中的型号
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 从 href 中提取
            if href:
                href_models = extract_models_from_text(href)
                models.update(href_models)

            # 从文本中提取
            if text:
                text_models = extract_models_from_text(text)
                models.update(text_models)

        # 3. 查找代码块中的型号
        code_blocks = soup.find_all(['code', 'pre'])
        for code in code_blocks:
            text = code.get_text()
            code_models = extract_models_from_text(text)
            models.update(code_models)

        # 4. 从整个页面文本中提取
        page_text = soup.get_text()
        page_models = extract_models_from_text(page_text)
        models.update(page_models)

        # 转换为排序后的列表
        sorted_models = sorted(list(models))

        logging.info(f"找到 {len(sorted_models)} 个有效的产品型号")

        # 保存到文件
        output_path = 'data/raw/model_list.json'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total_count': len(sorted_models),
                'models': sorted_models,
                'scraped_at': datetime.now().isoformat(),
                'prefix_rules': list(PREFIX_PATTERNS.keys())
            }, f, ensure_ascii=False, indent=2)

        logging.info(f"型号列表已保存到 {output_path}")

        # 打印所有找到的型号
        print("\n=== 抓取到的产品型号列表 ===")
        print(f"共找到 {len(sorted_models)} 个有效型号")
        print(f"使用的前缀规则: {', '.join(PREFIX_PATTERNS.keys())}")
        print()

        # 按前缀分组显示
        by_prefix = {}
        for model in sorted_models:
            for prefix in PREFIX_PATTERNS.keys():
                if model.startswith(prefix):
                    if prefix not in by_prefix:
                        by_prefix[prefix] = []
                    by_prefix[prefix].append(model)
                    break

        for prefix in sorted(by_prefix.keys()):
            models_list = by_prefix[prefix]
            print(f"\n=== {prefix} 系列型号 ({len(models_list)}个) ===")
            for i, model in enumerate(sorted(models_list), 1):
                print(f"{i:3d}. {model}")

        return sorted_models

    except requests.RequestException as e:
        logging.error(f"网络请求失败: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"抓取过程中发生错误: {str(e)}")
        raise

if __name__ == '__main__':
    scrape_qiachip_models()