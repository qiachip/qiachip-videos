"""
YouTube 视频元数据抓取工具
通过 YouTube Data API v3 抓取指定频道的所有视频
"""

import os
import json
import logging
import argparse
import time
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    抓取频道的所有视频
    Args:
        youtube: YouTube 服务客户端
        channel_id: YouTube 频道 ID
        max_results: 每次请求的最大结果数（默认50）
    Returns:
        list: 视频元数据列表
    """
    videos = []
    next_page_token = None
    total_fetched = 0

    logger.info(f"开始抓取频道 {channel_id} 的视频...")

    try:
        # 获取频道 ID（确保是有效的）
        get_channel_id(youtube, channel_id)

        # 获取频道上所有视频
        while True:
            playlist_request = lambda: youtube.playlistItems().list(
                part='contentDetails',
                playlistId=f'UU{channel_id[2:]}',  # 转换为播放列表 ID
                maxResults=max_results,
                pageToken=next_page_token
            ).execute()

            # 使用重试机制获取播放列表
            playlist_items_response = make_request_with_retry(playlist_request)

            # 获取视频详细信息
            video_ids = []
            for item in playlist_items_response['items']:
                video_ids.append(item['contentDetails']['videoId'])

            if video_ids:
                videos_request = lambda: youtube.videos().list(
                    part='id,snippet,statistics',
                    id=','.join(video_ids)
                ).execute()

                videos_response = make_request_with_retry(videos_request)

                for video in videos_response['items']:
                    video_data = {
                        'video_id': video['id'],
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],
                        'published_at': video['snippet']['publishedAt'],
                        'thumbnail_url': '',
                        'view_count': int(video.get('statistics', {}).get('viewCount', 0)),
                        'like_count': int(video.get('statistics', {}).get('likeCount', 0))
                    }

                    # 获取缩略图 URL
                    if 'thumbnails' in video['snippet']:
                        if 'high' in video['snippet']['thumbnails']:
                            video_data['thumbnail_url'] = video['snippet']['thumbnails']['high']['url']
                        elif 'medium' in video['snippet']['thumbnails']:
                            video_data['thumbnail_url'] = video['snippet']['thumbnails']['medium']['url']
                        elif 'default' in video['snippet']['thumbnails']:
                            video_data['thumbnail_url'] = video['snippet']['thumbnails']['default']['url']

                    videos.append(video_data)
                    total_fetched += 1
                    if total_fetched % 10 == 0:
                        logger.info(f"已抓取 {total_fetched} 个视频")

            # 检查是否有下一页
            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                logger.info(f"所有视频抓取完成，总共 {total_fetched} 个视频")
                break

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

        # 抓取视频
        videos = fetch_all_videos(youtube, args.channel_id)

        # 保存结果
        output_file = 'data/raw/raw_videos.json'
        save_to_json(videos, output_file)

        logger.info(f"总共抓取了 {len(videos)} 个视频")

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())