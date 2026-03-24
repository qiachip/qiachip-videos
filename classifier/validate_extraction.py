#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys

# 设置编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def extract_model_from_text(text: str) -> str:
    """提取产品型号"""
    if not text:
        return 'unclassified'

    # 改进的正则表达式模式
    pattern1 = r'\b[RXKTX]\d+[A-Z]{0,3}\b'
    pattern2 = r'\b[A-Z][A-Z0-9]{2,}\b'

    matches1 = re.findall(pattern1, text)
    if matches1:
        for match in matches1:
            if match not in ['LED', 'APP', 'USB', 'WIFI']:
                return match

    matches2 = re.findall(pattern2, text)
    if matches2:
        common_words = {'LED', 'APP', 'USB', 'WIFI', 'THE', 'AND', 'FOR', 'WITH', 'FROM',
                       'THIS', 'THAT', 'VIDEO', 'REVIEW', 'TEST', 'NEW', 'PRO', 'MAX',
                       'MIN', 'PLUS', 'ELITE', 'ULTRA', 'MEGA', 'GIGA', 'HOW', 'TO', 'DIY'}

        for match in matches2:
            if len(match) >= 3 and match not in common_words:
                return match

    return 'unclassified'

def main():
    # 加载数据
    with open('data/processed/videos_with_model.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)

    # 选择一些特定的视频来验证
    print("=== 验证提取结果 ===\n")

    # 1. 查看提取到 RX480E 的视频
    rx480e_videos = [v for v in videos if v['model'] == 'RX480E']
    print(f"找到 {len(rx480e_videos)} 个 RX480E 视频:")
    for video in rx480e_videos:
        print(f"  标题: {video['title']}")
        print(f"  描述片段: {video['description'][:100]}...")
        print()

    # 2. 查看一些标记为 unclassified 但可能包含型号的视频
    print("\n=== 可能被误分类为 unclassified 的视频 ===")
    sample_unclassified = videos[:20]  # 查看前20个
    for video in sample_unclassified:
        if video['model'] == 'unclassified':
            # 检查标题或描述中是否包含可能的型号
            title_matches = re.findall(r'\b[RXKTX]\d+[A-Z]{0,3}\b', video['title'])
            desc_matches = re.findall(r'\b[RXKTX]\d+[A-Z]{0,3}\b', video['description'])

            if title_matches or desc_matches:
                print(f"视频ID: {video['video_id']}")
                print(f"标题: {video['title']}")
                if title_matches:
                    print(f"标题中的匹配: {title_matches}")
                if desc_matches:
                    print(f"描述中的匹配: {desc_matches}")
                print()

if __name__ == '__main__':
    main()