from django.core.management.base import BaseCommand
from youtube.services import YouTubeService
import json


class Command(BaseCommand):
    help = "Test the YouTube API service"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="The search query to test")
        parser.add_argument(
            "--results", type=int, default=5, help="Number of results to return"
        )

    def handle(self, *args, **kwargs):
        query = kwargs["query"]
        max_results = kwargs["results"]

        self.stdout.write(
            self.style.SUCCESS(f'Testing YouTube API with query: "{query}"')
        )

        service = YouTubeService()
        videos = service.search_videos(query, max_results=max_results)

        if not videos:
            self.stdout.write(self.style.WARNING("No videos found!"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(videos)} videos:"))

        # Pretty print the results
        for i, video in enumerate(videos):
            self.stdout.write(self.style.SUCCESS(f"\n{i+1}. {video['title']}"))
            self.stdout.write(f"   Channel: {video['channel_title']}")
            self.stdout.write(f"   Published: {video['published_at']}")
            self.stdout.write(f"   YouTube ID: {video['youtube_id']}")
            self.stdout.write(f"   Thumbnail: {video['thumbnail_url']}")
            if "duration" in video:
                self.stdout.write(f"   Duration: {video['duration']}")
            if "view_count" in video:
                self.stdout.write(f"   Views: {video['view_count']}")

        self.stdout.write(self.style.SUCCESS("\nAPI test completed successfully!"))
