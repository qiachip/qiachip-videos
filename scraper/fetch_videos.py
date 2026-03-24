"""
修复版 YouTube 视频元数据抓取工具
解决 SSL/TLS 兼容性问题
"""

import os
import json
import logging
import argparse
import time
import ssl
import urllib.request
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# 配置日志
# 设置控制台编码为 UTF-8 以避免中文乱码
import sys
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach(), 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach(), 'strict')
    except:
        pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 修复 SSL 上下文
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # 如果不存在这个方法，说明版本可能不同
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def load_api_key():
    """从环境变量加载 YouTube API 密钥"""
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        logger.error("YOUTUBE_API_KEY 未在环境变量中找到")
        raise ValueError("请设置 YOUTUBE_API_KEY 环境变量")
    return api_key

def create_youtube_service(api_key):
    """创建 YouTube 服务客户端"""
    try:
        # 创建服务时设置超时参数
        youtube = build(
            'youtube',
            'v3',
            developerKey=api_key,
            cache_discovery=False  # 禁用发现缓存以避免一些连接问题
        )
        logger.info("YouTube 服务创建成功")
        return youtube
    except Exception as e:
        logger.error(f"创建 YouTube 服务失败: {e}")
        raise

def get_channel_id(youtube, channel_identifier):
    """通过用户名或 ID 获取频道 ID"""
    try:
        # 尝试作为用户名查询
        channels_response = youtube.channels().list(
            part='id',
            forUsername=channel_identifier
        ).execute()

        if 'items' in channels_response:
            logger.info(f"通过用户名找到频道: {channel_identifier}")
            return channels_response['items'][0]['id']

        # 尝试作为频道 ID 查询
        channels_response = youtube.channels().list(
            part='id',
            id=channel_identifier
        ).execute()

        if 'items' in channels_response:
            logger.info(f"通过 ID 找到频道: {channel_identifier}")
            return channel_identifier

        raise ValueError(f"找不到频道: {channel_identifier}")

    except Exception as e:
        logger.error(f"获取频道 ID 失败: {e}")
        raise

def make_request_with_retry(request_func, max_retries=3, delay=2):
    """带重试机制的请求函数"""
    for attempt in range(max_retries):
        try:
            return request_func()
        except HttpError as e:
            if e.resp.status == 403:
                logger.error("API 配额限制，请稍后再试")
                raise
            elif e.resp.status == 429:
                logger.warning(f"请求太频繁，等待 {delay} 秒后重试")
                time.sleep(delay * (attempt + 1))
                continue
            else:
                logger.error(f"HTTP 错误: {e}")
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"达到最大重试次数，失败: {e}")
                raise
            logger.warning(f"请求失败，{delay} 秒后重试 (尝试 {attempt + 1}/{max_retries})")
            time.sleep(delay * (attempt + 1))

def fetch_all_videos(youtube, channel_id, max_results=50):
    """
    分两步获取频道的所有视频数据
    第一步：获取所有 video_id
    第二步：批量获取完整元数据
    """
    video_ids = []
    videos = []

    logger.info(f"开始分步获取频道 {channel_id} 的视频...")

    try:
        # 步骤1：获取频道 ID
        actual_channel_id = get_channel_id(youtube, channel_id)
        logger.info(f"使用频道 ID: {actual_channel_id}")

        # 步骤1.1：获取频道的上传列表 ID
        logger.info("步骤1：获取频道的上传列表 ID...")
        channels_response = make_request_with_retry(lambda: youtube.channels().list(
            part='contentDetails',
            id=actual_channel_id
        ).execute())

        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        logger.info(f"找到上传列表 ID: {uploads_playlist_id}")

        # 步骤1.2：翻页获取所有 video_id
        next_page_token = None
        total_ids = 0

        while True:
            playlist_request = lambda: youtube.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=max_results,
                pageToken=next_page_token
            ).execute()

            playlist_items_response = make_request_with_retry(playlist_request)

            # 提取视频 ID
            for item in playlist_items_response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            total_ids = len(video_ids)
            logger.info(f"已获取 {total_ids} 个视频 ID")

            # 检查是否有下一页
            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                break

        logger.info(f"步骤1完成：共获取 {total_ids} 个视频 ID")

        # 步骤2：批量获取视频元数据
        logger.info("步骤2：批量获取视频元数据...")
        batch_size = 50  # API 每次最多50个视频
        total_batches = (len(video_ids) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(video_ids))
            batch_ids = video_ids[start_idx:end_idx]

            logger.info(f"处理批次 {batch_num + 1}/{total_batches}: {len(batch_ids)} 个视频")

            videos_request = lambda batch=batch_ids: youtube.videos().list(
                part='snippet,statistics',
                id=','.join(batch)
            ).execute()

            videos_response = make_request_with_retry(videos_request)

            # 提取视频信息
            for video in videos_response['items']:
                video_data = {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'published_at': video['snippet']['publishedAt'],
                    'thumbnail_url': '',
                    'view_count': 0,
                    'like_count': 0
                }

                # 获取缩略图 URL（优先使用 high，其次是 medium）
                if 'thumbnails' in video['snippet']:
                    if 'high' in video['snippet']['thumbnails']:
                        video_data['thumbnail_url'] = video['snippet']['thumbnails']['high']['url']
                    elif 'medium' in video['snippet']['thumbnails']:
                        video_data['thumbnail_url'] = video['snippet']['thumbnails']['medium']['url']
                    elif 'default' in video['snippet']['thumbnails']:
                        video_data['thumbnail_url'] = video['snippet']['thumbnails']['default']['url']

                # 从 statistics 获取统计数据（可能不存在）
                if 'statistics' in video:
                    video_data['view_count'] = int(video['statistics'].get('viewCount', 0))
                    video_data['like_count'] = int(video['statistics'].get('likeCount', 0))

                videos.append(video_data)

        logger.info(f"步骤2完成：成功获取 {len(videos)} 个视频的完整元数据")

    except Exception as e:
        logger.error(f"抓取视频时发生错误: {e}")
        raise

    return videos

def save_to_json(data, filename):
    """保存数据到 JSON 文件"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到 {filename}")
    except Exception as e:
        logger.error(f"保存文件时发生错误: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='抓取 YouTube 频道视频元数据')
    parser.add_argument('channel_id', help='YouTube 频道 ID 或用户名')

    args = parser.parse_args()

    try:
        # 加载 API 密钥
        api_key = load_api_key()

        # 创建 YouTube 服务
        youtube = create_youtube_service(api_key)

        # 获取频道 ID
        channel_id = get_channel_id(youtube, args.channel_id)
        logger.info(f"使用频道 ID: {channel_id}")

        # 抓取视频
        videos = fetch_all_videos(youtube, channel_id)

        # 保存结果
        output_file = 'data/raw/raw_videos.json'
        save_to_json(videos, output_file)

        logger.info(f"程序完成，共抓取 {len(videos)} 个视频")

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())