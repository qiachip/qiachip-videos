#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

# 设置编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    # 加载数据
    with open('data/processed/videos_with_model.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)

    print("=== 匹配结果示例 ===\n")

    # 1. 展示成功匹配多个型号的视频
    multi_model_videos = []
    for video in videos:
        model = video.get('model')
        if model != 'unclassified' and ',' in model:
            multi_model_videos.append(video)

    if multi_model_videos:
        print("匹配到多个型号的视频:")
        for i, video in enumerate(multi_model_videos[:3], 1):
            print(f"\n视频 {i}:")
            print(f"型号: {video['model']}")
            print(f"标题: {video['title'][:100]}...")

    # 2. 展示只匹配到单个型号的视频
    single_model_videos = []
    for video in videos:
        model = video.get('model')
        if model != 'unclassified' and ',' not in model:
            single_model_videos.append(video)

    print(f"\n匹配到单个型号的视频（展示前5个）:")
    for i, video in enumerate(single_model_videos[:5], 1):
        print(f"\n视频 {i}:")
        print(f"型号: {video['model']}")
        print(f"标题: {video['title'][:100]}...")

    # 3. 展示未匹配的视频
    unclassified_videos = []
    for video in videos:
        if video.get('model') == 'unclassified':
            unclassified_videos.append(video)

    print(f"\n未匹配型号的视频（展示前3个）:")
    for i, video in enumerate(unclassified_videos[:3], 1):
        print(f"\n视频 {i}:")
        print(f"标题: {video['title'][:100]}...")
        print(f"描述片段: {video['description'][:100]}...")

if __name__ == '__main__':
    main()