# `qiachip-videos`

> 一个智能工具，能够自动识别 YouTube 视频对应的产品型号，帮助品牌快速整理和管理产品宣传视频。本项目的完整描述为：`Qiachip YouTube Product Video Smart Classification`。

![分类准确率](https://img.shields.io/badge/准确率-97.8%25-green)
![已分类](https://img.shields.io/badge/已分类-274%2F280-blue)
![Python](https://img.shields.io/badge/Python-3.11-yellow)

## 项目概述

qiachip-videos 项目通过五层智能分类流水线，将 YouTube 频道自动化识别产品型号，大幅提升视频内容管理效率。

**当前状态：**
- 分类准确率：**97.8%** (274/280)
- 待分类视频：6 条
- 多型号视频：10 条（收藏夹或混合型号）

## 项目结构

```
qiachip-lens/
├── classifier/              # 分类核心代码
│   ├── extract_model.py     # 五层分类流水线
│   ├── match_models.py      # 模型匹配逻辑
│   └── ...                  # 其他辅助脚本
├── data/
│   ├── raw/                 # 原始数据
│   │   ├── raw_videos.json  # YouTube 抓取的视频数据
│   │   └── model_list.json  # 产品型号白名单
│   └── processed/           # 处理后的数据
│       └── videos_with_model.json  # 分类结果
├── reports/
│   └── dashboard.html       # 可视化仪表板
├── CLAUDE.md                # Claude AI 开发指南
└── README.md                # 本文件
```

## 快速开始

### 1. 运行分类器

```bash
python classifier/extract_model.py
```

执行后会自动处理 `data/raw/raw_videos.json` 中的视频数据，输出到 `data/processed/videos_with_model.json`。

### 2. 查看仪表板

双击打开 `reports/dashboard.html` 即可在浏览器中查看分类结果可视化。

## 分类原理（五层流水线）

系统按优先级依次执行以下匹配：

| 层级 | 名称 | 说明 | 示例 |
|------|------|------|------|
| 0 | **手动标注** | 最高优先级，人工确认的映射 | `VIDEO_ID_MAP["abc123"] = ("KR2201-4", "manual")` |
| 1 | **精确匹配** | 白名单型号完全匹配（忽略大小写） | 标题中包含 `KR2201-4` → 匹配 |
| 2 | **正则匹配** | 识别 KR/RX/TX 等前缀格式型号 | 标题中包含 `RX480E-868` → 匹配 |
| 3 | **关键词匹配** | 特征词组合推断型号 | `dc12v + 433mhz + 1-ch` → `KR1201A` |
| 4 | **自动标签** | 识别工厂视频/无关内容 | `packing work` → `factory_content` |

**匹配顺序**：先扫描标题，标题未命中再扫描描述文本。

## 支持的分类结果

| 类型 | 说明 | 示例 |
|------|------|------|
| **具体型号** | 确认的单一产品型号 | `KR1201`、`KR2201-4`、`RX480E` |
| **多型号** | 无法区分时返回多个候选 | `KR1201A,KR1201C` |
| **特殊标签** | 非产品型号内容 | `factory_content`（工厂视频）、`off_topic`（无关内容） |
| **未分类** | 系统无法识别 | `unclassified` |

## 手动修正分类

如果自动分类不准确，可在 `classifier/extract_model.py` 的 `VIDEO_ID_MAP` 字典中添加手动映射：

```python
VIDEO_ID_MAP = {
    # 格式："视频ID": ("正确型号", "manual")
    "ABC123xyz45": ("KR2201-4", "manual"),
    "DEF678xyz45": ("off_topic", "auto_label"),
}
```

**视频ID获取方式**：YouTube 链接中 `?v=` 后面的 11 位字符。

例如：`https://www.youtube.com/watch?v=7J1MdAHxLdc` 的视频ID是 `7J1MdAHxLdc`。

## 数据文件说明

| 文件路径 | 用途 |
|----------|------|
| `data/raw/raw_videos.json` | 原始视频数据（从 YouTube API 获取） |
| `data/raw/model_list.json` | 产品型号白名单 |
| `data/processed/videos_with_model.json` | 分类后的结果数据 |

## 常见问题

### Q: 视频被错误分类怎么办？

在 `classifier/extract_model.py` 的 `VIDEO_ID_MAP` 中添加手动映射即可覆盖自动结果。

### Q: 如何查看某个型号有哪些视频？

打开 `reports/dashboard.html`，点击对应型号的饼图区域即可筛选。

### Q: 数据如何更新？

将新视频数据追加到 `data/raw/raw_videos.json`，重新运行 `extract_model.py` 即可。

### Q: 为什么某些视频返回多个型号？

当系统无法区分相似型号（如 KR1201A 和 KR1201C）时，会返回所有可能的候选。这是符合预期的行为。

## 技术栈

- **语言**：Python 3.11
- **核心库**：标准库（无需额外依赖）
- **前端**：原生 HTML/JS（零外部依赖）

## 许可证

本项目为 Qiachip 内部工具，版权所有。