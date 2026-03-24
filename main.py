#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import os
import subprocess
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_step(step_name, command, step_num, total_steps):
    """运行单个步骤并计时"""
    print(f"\n[{step_num}/{total_steps}] 正在{step_name}...")
    start_time = time.time()

    try:
        # 使用 subprocess 运行，以便实时看到输出
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 实时打印子进程输出
        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode != 0:
            print(f"\n❌ {step_name}失败 (退出码: {process.returncode})")
            return False, 0

    except Exception as e:
        print(f"\n❌ 执行{step_name}时发生异常: {e}")
        return False, 0

    duration = time.time() - start_time
    print(f"✅ {step_name}完成，耗时: {duration:.2f}秒")
    return True, duration

def main():
    print("=" * 50)
    print("   Qiachip Lens 视频分类系统")
    print("=" * 50)
    print("\n请选择运行模式：")
    print("1. 完整流程（抓视频 → 抓文档 → 分类 → 导出）")
    print("2. 新视频已发布（抓视频 → 分类 → 导出，跳过抓文档）")
    print("3. 说明书文档已更新（抓文档 → 分类 → 导出，跳过抓视频）")
    print("4. 仅重新分类导出（直接用现有数据，只跑分类 → 导出）")

    mode = ""
    while mode not in ["1", "2", "3", "4"]:
        mode = input("\n请输入数字 (1-4): ").strip()
        if mode not in ["1", "2", "3", "4"]:
            print("无效输入，请重新输入。")

    # 定义步骤
    # 步骤命令定义
    cmd_fetch_videos = "python scraper/fetch_videos.py Qiachip"
    cmd_fetch_docs = "python scraper/fetch_model_docs.py"
    cmd_classify = "python classifier/extract_model.py"
    cmd_dashboard_v1 = "python scripts/generate_dashboard.py"
    cmd_dashboard_v2 = "python scripts/generate_dashboard_v2.py"

    steps = []
    if mode == "1":
        steps = [
            ("抓取 YouTube 视频", cmd_fetch_videos),
            ("抓取说明书文档", cmd_fetch_docs),
            ("执行视频分类", cmd_classify),
            ("生成仪表盘 V1", cmd_dashboard_v1),
            ("生成仪表盘 V2", cmd_dashboard_v2)
        ]
    elif mode == "2":
        steps = [
            ("抓取 YouTube 视频", cmd_fetch_videos),
            ("执行视频分类", cmd_classify),
            ("生成仪表盘 V1", cmd_dashboard_v1),
            ("生成仪表盘 V2", cmd_dashboard_v2)
        ]
    elif mode == "3":
        steps = [
            ("抓取说明书文档", cmd_fetch_docs),
            ("执行视频分类", cmd_classify),
            ("生成仪表盘 V1", cmd_dashboard_v1),
            ("生成仪表盘 V2", cmd_dashboard_v2)
        ]
    elif mode == "4":
        steps = [
            ("执行视频分类", cmd_classify),
            ("生成仪表盘 V1", cmd_dashboard_v1),
            ("生成仪表盘 V2", cmd_dashboard_v2)
        ]

    total_steps = len(steps)
    total_start_time = time.time()
    step_durations = []

    success = True
    for i, (name, cmd) in enumerate(steps):
        ok, duration = run_step(name, cmd, i + 1, total_steps)
        if not ok:
            success = False
            break
        step_durations.append((name, duration))

    total_duration = time.time() - total_start_time

    print("\n" + "=" * 50)
    if success:
        print("🎉 全部任务已成功完成！")
    else:
        print("⚠️ 流程中断，请检查上方错误信息。")

    print(f"\n总计耗时: {total_duration:.2f}秒")
    print("\n分步耗时统计:")
    for name, duration in step_durations:
        print(f" - {name}: {duration:.2f}秒")

    if success:
        # 如果分类步骤运行了，打印最后的统计信息摘要（从日志或输出中提取逻辑过于复杂，
        # 既然已经实时打印了 extract_model.py 的输出，用户已经能看到统计了。）
        print("\n分类结果已更新，请查看 reports 目录下的仪表盘文件。")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
