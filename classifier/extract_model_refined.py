#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
from typing import List, Dict, Optional, Set
import logging
import sys

# 设置编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extract_model_refined.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_raw_videos(file_path: str) -> List[Dict]:
    """加载原始视频数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"成功加载 {len(data)} 条视频数据")
            return data
    except Exception as e:
        logging.error(f"加载文件时发生错误: {str(e)}")
        raise

def extract_model_with_context(text: str) -> Optional[str]:
    """结合上下文的型号提取"""
    if not text:
        return None

    # 定义已知的 QIACHIP 产品型号（从之前的分析中得出的主要型号）
    known_models = {
        'RX480E', 'RX480', 'KR2202', 'KR1201', 'KR2302', 'KR2201', 'KR2201WB',
        'KR2201B', 'KR3001', 'KR1204', 'KR0548', 'KR2402', 'KT29', 'TX118SA',
        'DC12V', 'DC24V', 'DC5V', 'DC3V', 'DC6V', 'USB5V', 'AC110V'
    }

    # 匹配 QIACHIP 标准型号的规则
    pattern_qiachip = r'\b[RXKTX]\d+[A-Z]{0,3}\b'
    pattern_other = r'\b(?:DC|USB|AC)\d*[V]\b'  # 电压型号

    # 优先匹配已知型号
    for model in known_models:
        if model in text:
            return model

    # 匹配 QIACHIP 型号
    matches_qiachip = re.findall(pattern_qiachip, text)
    if matches_qiachip:
        # 过滤掉明显不是型号的
        valid_matches = [m for m in matches_qiachip if m not in ['LED', 'APP', 'USB', 'WIFI']]
        if valid_matches:
            return valid_matches[0]

    # 匹配电压型号
    matches_voltage = re.findall(pattern_other, text)
    if matches_voltage:
        return matches_voltage[0]

    # 最后尝试其他可能的型号
    pattern_general = r'\b[A-Z][A-Z0-9]{2,}\b'
    matches = re.findall(pattern_general, text)

    # 过滤掉常见词
    common_words = {'LED', 'APP', 'USB', 'WIFI', 'THE', 'AND', 'FOR', 'WITH', 'FROM',
                   'THIS', 'THAT', 'VIDEO', 'REVIEW', 'TEST', 'NEW', 'PRO', 'MAX',
                   'MIN', 'PLUS', 'ELITE', 'ULTRA', 'MEGA', 'GIGA', 'HOW', 'TO', 'DIY',
                   'THIS', 'IS', 'ARE', 'YOU', 'YOUR', 'CAN', 'WILL', 'BE', 'HAVE',
                   'FROM', 'THAT', 'THEY', 'THEM', 'THEIR', 'WHAT', 'WHICH', 'WHEN',
                   'WHERE', 'WHY', 'HOW', 'ALL', 'SOME', 'MANY', 'MORE', 'MOST', 'LESS'}

    # 优先选择出现在标题中的
    title_matches = [m for m in matches if m not in common_words and len(m) >= 3]
    if title_matches:
        return title_matches[0]

    return None

def extract_model_from_video(video_data: Dict) -> str:
    """从视频数据中提取型号"""
    title = video_data.get('title', '')
    description = video_data.get('description', '')

    # 从标题提取
    model = extract_model_with_context(title)
    if model:
        return model

    # 从描述提取
    model = extract_model_with_context(description)
    if model:
        return model

    # 都没有，标记为 unclassified
    return 'unclassified'

def save_processed_videos(data: List[Dict], file_path: str):
    """保存处理后的视频数据"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"成功保存处理后的数据到 {file_path}")
    except Exception as e:
        logging.error(f"保存文件时发生错误: {str(e)}")
        raise

def analyze_models_distribution(data: List[Dict]) -> Dict[str, int]:
    """分析型号分布"""
    model_counts = {}
    for video in data:
        model = video.get('model', 'unclassified')
        model_counts[model] = model_counts.get(model, 0) + 1
    return model_counts

def main():
    """主函数"""
    # 文件路径
    raw_videos_path = 'data/raw/raw_videos.json'
    processed_videos_path = 'data/processed/videos_with_model_refined.json'

    # 加载原始数据
    raw_videos = load_raw_videos(raw_videos_path)

    # 提取型号
    processed_videos = []
    total_videos = len(raw_videos)

    for i, video in enumerate(raw_videos, 1):
        if i % 50 == 0 or i == 1:
            logging.info(f"正在处理第 {i}/{total_videos} 个视频...")

        video_copy = video.copy()
        video_copy['model'] = extract_model_from_video(video)
        processed_videos.append(video_copy)

    # 保存处理后的数据
    save_processed_videos(processed_videos, processed_videos_path)

    # 分析型号分布
    model_distribution = analyze_models_distribution(processed_videos)
    sorted_models = sorted(model_distribution.items(), key=lambda x: x[1], reverse=True)

    # 输出统计结果
    print("\n=== 精炼后的型号分布统计 ===")
    for model, count in sorted_models:
        percentage = (count / total_videos) * 100
        print(f"{model}: {count} ({percentage:.1f}%)")

    # 统计改进
    unclassified_count = model_distribution.get('unclassified', 0)
    unclassified_percentage = (unclassified_count / total_videos) * 100
    print(f"\n未分类视频: {unclassified_count} ({unclassified_percentage:.1f}%)")

    # 显示主要型号
    print("\n=== 主要型号统计 ===")
    main_models = {k: v for k, v in model_distribution.items() if v >= 5}
    for model, count in sorted(main_models.items(), key=lambda x: x[1], reverse=True):
        print(f"{model}: {count}个视频")

if __name__ == '__main__':
    main()