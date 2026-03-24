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

    # 收集所有型号
    all_models = set()
    multi_model_count = 0

    for video in videos:
        model = video.get('model', 'unclassified')
        if model != 'unclassified':
            if ',' in model:
                multi_model_count += 1
                models = model.split(',')
                for m in models:
                    all_models.add(m)
            else:
                all_models.add(model)

    # 排序并打印
    print("=== 所有提取到的产品型号 ===")
    print(f"总型号数: {len(all_models)}")
    print(f"多个型号的视频数: {multi_model_count}")
    print()

    for i, model in enumerate(sorted(list(all_models)), 1):
        print(f"{i:3d}. {model}")

if __name__ == '__main__':
    main()