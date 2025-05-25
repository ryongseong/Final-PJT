from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import isodate
import logging
import json
import pytz

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service class for YouTube API operations"""

    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        try:
            # Log API key (masked) for debugging
            masked_key = (
                self.api_key[:4] + "..." + self.api_key[-4:]
                if len(self.api_key) > 8
                else "****"
            )
            logger.info(f"Initializing YouTube service with API key: {masked_key}")

            self.youtube = build(
                "youtube", "v3", developerKey=self.api_key, static_discovery=False
            )
        except Exception as e:
            logger.error(f"Error initializing YouTube service: {str(e)}")
            self.youtube = None

    def search_videos(self, query, max_results=10):
        """
        Search for videos on YouTube based on a query
        Specifically tailored for stock-related content
        """
        try:
            # Add stock-specific terms to the query for better results
            stock_query = f"{query} stocks finance investing"

            logger.info(f"Searching YouTube for: {stock_query}")

            if not self.youtube:
                logger.error("YouTube API client not initialized")
                return []

            search_response = (
                self.youtube.search()
                .list(
                    q=stock_query,
                    part="id,snippet",
                    maxResults=max_results,
                    type="video",
                    regionCode="KR",
                    safeSearch="moderate",
                )
                .execute()
            )

            video_ids = [
                item["id"]["videoId"] for item in search_response.get("items", [])
            ]

            if not video_ids:
                logger.warning(f"No video IDs found for query: {query}")
                return []

            # Get additional video details
            logger.info(f"Fetching details for {len(video_ids)} videos")
            videos_response = (
                self.youtube.videos()
                .list(part="contentDetails,statistics,snippet", id=",".join(video_ids))
                .execute()
            )

            videos = []
            for item in videos_response.get("items", []):
                # Parse the datetime string and make it timezone-aware
                naive_published_at = datetime.strptime(
                    item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                )
                # Convert to aware datetime with UTC timezone
                aware_published_at = pytz.utc.localize(naive_published_at)
                # Convert to the project's timezone if needed
                published_at = aware_published_at.astimezone(
                    timezone.get_current_timezone()
                )

                # Handle missing statistics data
                statistics = item.get("statistics", {})
                view_count = statistics.get("viewCount", 0)

                video_data = {
                    "youtube_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                    "published_at": published_at,
                    "channel_title": item["snippet"]["channelTitle"],
                    "search_query": query,
                    "duration": str(
                        isodate.parse_duration(item["contentDetails"]["duration"])
                    ),
                    "view_count": view_count,
                }
                videos.append(video_data)

            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos

        except HttpError as e:
            error_content = json.loads(e.content.decode())
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(
                f"YouTube API error: {error_message} (status: {e.status_code})"
            )
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {str(e)}")
            return []

    def get_related_videos(self, video_id, max_results=5):
        """
        Get related videos for a specific YouTube video
        """
        try:
            logger.info(f"Fetching related videos for YouTube ID: {video_id}")

            if not self.youtube:
                logger.error("YouTube API client not initialized")
                return []

            # Get related videos
            search_response = (
                self.youtube.search()
                .list(
                    relatedToVideoId=video_id,
                    part="id,snippet",
                    maxResults=max_results,
                    type="video",
                )
                .execute()
            )

            video_ids = [
                item["id"]["videoId"] for item in search_response.get("items", [])
            ]

            if not video_ids:
                logger.warning(f"No related videos found for video ID: {video_id}")
                return []

            # Get additional video details
            videos_response = (
                self.youtube.videos()
                .list(part="contentDetails,statistics,snippet", id=",".join(video_ids))
                .execute()
            )

            videos = []
            for item in videos_response.get("items", []):
                # Parse the datetime string and make it timezone-aware
                naive_published_at = datetime.strptime(
                    item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                )
                # Convert to aware datetime with UTC timezone
                aware_published_at = pytz.utc.localize(naive_published_at)
                # Convert to the project's timezone if needed
                published_at = aware_published_at.astimezone(
                    timezone.get_current_timezone()
                )

                video_data = {
                    "youtube_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                    "published_at": published_at,
                    "channel_title": item["snippet"]["channelTitle"],
                }
                videos.append(video_data)

            logger.info(f"Found {len(videos)} related videos for video ID: {video_id}")
            return videos

        except HttpError as e:
            error_content = json.loads(e.content.decode())
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(
                f"YouTube API error in related videos: {error_message} (status: {e.status_code})"
            )
            return []
        except Exception as e:
            logger.error(f"Error getting related YouTube videos: {str(e)}")
            return []
