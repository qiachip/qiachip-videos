# Qiachip Lens

一个用于抓取 YouTube 频道视频元数据并按产品型号分类的工具。

## 项目结构

```
qiachip-lens/
├── scraper/          # YouTube 数据抓取模块
├── classifier/       # 产品型号分类模块
├── data/            # 数据存储
│   ├── raw/         # 原始数据
│   └── processed/   # 处理后的数据
├── tests/           # 测试模块
├── notebooks/       # Jupyter 笔记本
├── requirements.txt # Python 依赖
└── .env.example     # 环境变量示例
```

## 功能特性

- 通过 YouTube API 抓取频道视频元数据
- 自动按产品型号对视频进行分类
- 支持数据导出到 Excel 格式
- 包含完整的测试套件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并填入您的 YouTube API 密钥：

```bash
cp .env.example .env
```

## 使用方法

请参考各模块的文档说明了解具体的使用方法。