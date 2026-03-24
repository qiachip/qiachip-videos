#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import List, Dict, Set
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
        logging.FileHandler('match_models.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_model_whitelist(file_path: str) -> Set[str]:
    """加载型号白名单"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            models = set(data['models'])
            logging.info(f"加载白名单型号: {len(models)} 个")
            return models
    except Exception as e:
        logging.error(f"加载白名单失败: {str(e)}")
        raise

def load_raw_videos(file_path: str) -> List[Dict]:
    """加载原始视频数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"加载视频数据: {len(data)} 个")
            return data
    except Exception as e:
        logging.error(f"加载视频数据失败: {str(e)}")
        raise

def match_models_in_text(text: str, model_whitelist: Set[str]) -> List[str]:
    """在文本中匹配白名单中的型号（忽略大小写）"""
    if not text:
        return []

    matched_models = []

    # 转换为小写进行匹配
    text_lower = text.lower()

    for model in model_whitelist:
        # 转换模型为小写进行匹配
        model_lower = model.lower()

        # 使用单词边界确保完整匹配
        # 例如：KR1201 不会被 KR1201A 匹配
        if re.search(r'\b' + re.escape(model_lower) + r'\b', text_lower):
            matched_models.append(model)

    return matched_models

def process_videos(raw_videos: List[Dict], model_whitelist: Set[str]) -> List[Dict]:
    """处理视频数据，添加模型匹配"""
    processed_videos = []

    for i, video in enumerate(raw_videos, 1):
        if i % 50 == 0 or i == 1:
            logging.info(f"正在处理第 {i}/{len(raw_videos)} 个视频...")

        # 复制原始数据
        video_copy = video.copy()

        # 获取标题和描述
        title = video_copy.get('title', '')
        description = video_copy.get('description', '')

        # 合并文本进行匹配
        combined_text = f"{title} {description}"

        # 匹配型号
        matched_models = match_models_in_text(combined_text, model_whitelist)

        if matched_models:
            # 如果匹配到多个型号，用逗号连接
            video_copy['model'] = ','.join(matched_models)
            logging.debug(f"视频 {video_copy['video_id']}: 匹配到 {len(matched_models)} 个型号 - {matched_models}")
        else:
            video_copy['model'] = 'unclassified'
            logging.debug(f"视频 {video_copy['video_id']}: 未匹配到型号")

        processed_videos.append(video_copy)

    return processed_videos

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

def analyze_results(data: List[Dict]):
    """分析匹配结果"""
    model_stats = {}
    unclassified_count = 0

    for video in data:
        model = video.get('model', 'unclassified')

        if model == 'unclassified':
            unclassified_count += 1
        else:
            # 统计每个型号的出现次数
            models = model.split(',')
            for m in models:
                model_stats[m] = model_stats.get(m, 0) + 1

    # 输出统计结果
    total_videos = len(data)
    unclassified_percentage = (unclassified_count / total_videos) * 100

    print("\n=== 匹配结果统计 ===")
    print(f"总视频数: {total_videos}")
    print(f"已匹配: {total_videos - unclassified_count} ({(100 - unclassified_percentage):.1f}%)")
    print(f"未匹配: {unclassified_count} ({unclassified_percentage:.1f}%)")

    # 按出现次数排序
    sorted_models = sorted(model_stats.items(), key=lambda x: x[1], reverse=True)

    print("\n=== 型号出现次数统计 ===")
    for model, count in sorted_models:
        percentage = (count / total_videos) * 100
        print(f"{model}: {count} ({percentage:.1f}%)")

    # 显示每个型号的视频数量
    print(f"\n共找到 {len(model_stats)} 个不同的型号")

def main():
    """主函数"""
    # 文件路径
    model_list_path = 'data/raw/model_list.json'
    raw_videos_path = 'data/raw/raw_videos.json'
    processed_videos_path = 'data/processed/videos_with_model.json'

    # 加载数据
    model_whitelist = load_model_whitelist(model_list_path)
    raw_videos = load_raw_videos(raw_videos_path)

    # 处理视频
    processed_videos = process_videos(raw_videos, model_whitelist)

    # 保存结果
    save_processed_videos(processed_videos, processed_videos_path)

    # 分析结果
    analyze_results(processed_videos)

if __name__ == '__main__':
    main()