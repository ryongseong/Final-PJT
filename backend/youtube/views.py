from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import YouTubeVideo, SavedVideo
from .serializers import (
    YouTubeVideoSerializer,
    SavedVideoSerializer,
    SavedVideoCreateSerializer,
)
from .services import YouTubeService
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class YouTubeViewSet(viewsets.ModelViewSet):
    queryset = YouTubeVideo.objects.all()
    serializer_class = YouTubeVideoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "channel_title"]
    ordering_fields = ["published_at", "created_at"]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def search(self, request):
        """Search for videos on YouTube based on a query"""
        query = request.query_params.get("q", "")
        logger.info(f"YouTube search requested for query: {query}")

        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = YouTubeService()
            videos = service.search_videos(query)

            if not videos:
                logger.warning(f"No videos found for query: {query}")
                return Response(
                    {"message": "No videos found for this query"},
                    status=status.HTTP_204_NO_CONTENT,
                )

            # Save the videos to the database for later reference
            saved_videos = []
            with transaction.atomic():
                for video_data in videos:
                    # Get or create the video in the database
                    video, created = YouTubeVideo.objects.update_or_create(
                        youtube_id=video_data["youtube_id"],
                        defaults={
                            "title": video_data["title"],
                            "description": video_data["description"],
                            "thumbnail_url": video_data["thumbnail_url"],
                            "published_at": video_data["published_at"],
                            "channel_title": video_data["channel_title"],
                            "search_query": query,
                        },
                    )
                    saved_videos.append(video)

            serializer = self.get_serializer(saved_videos, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in YouTube search: {str(e)}")
            return Response(
                {"error": "An error occurred while searching YouTube videos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def get_by_youtube_id(self, request):
        """Get video details by YouTube ID"""
        youtube_id = request.query_params.get("id", "")

        if not youtube_id:
            return Response(
                {"error": "YouTube ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            video = YouTubeVideo.objects.filter(youtube_id=youtube_id).first()
            if not video:
                return Response(
                    {"error": "Video not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.get_serializer(video)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving video by YouTube ID {youtube_id}: {str(e)}")
            return Response(
                {"error": "Failed to retrieve video"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def related_videos(self, request):
        """Get related videos for a specific YouTube video"""
        youtube_id = request.query_params.get("id", "")

        if not youtube_id:
            return Response(
                {"error": "YouTube ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = YouTubeService()
            videos = service.get_related_videos(youtube_id)

            if not videos:
                logger.warning(f"No related videos found for YouTube ID: {youtube_id}")
                return Response(
                    {"message": "No related videos found"},
                    status=status.HTTP_204_NO_CONTENT,
                )

            # Save the videos to the database for later reference
            saved_videos = []
            with transaction.atomic():
                for video_data in videos:
                    video, created = YouTubeVideo.objects.update_or_create(
                        youtube_id=video_data["youtube_id"],
                        defaults={
                            "title": video_data["title"],
                            "description": video_data["description"],
                            "thumbnail_url": video_data["thumbnail_url"],
                            "published_at": video_data["published_at"],
                            "channel_title": video_data["channel_title"],
                            "search_query": f"related_to_{youtube_id}",
                        },
                    )
                    saved_videos.append(video)

            serializer = self.get_serializer(saved_videos, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(
                f"Error retrieving related videos for YouTube ID {youtube_id}: {str(e)}"
            )
            return Response(
                {"error": "Failed to retrieve related videos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SavedVideoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return SavedVideo.objects.filter(user=self.request.user).select_related("video")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return SavedVideoCreateSerializer
        return SavedVideoSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, saved_at=timezone.now())
        logger.info(
            f"New video saved successfully by user {self.request.user.username}"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Check if this video is already saved by the current user
            video_id = serializer.validated_data.get("video").id
            existing_saved = SavedVideo.objects.filter(
                user=request.user, video_id=video_id
            ).exists()

            if existing_saved:
                # Video already saved, just update the notes if provided
                saved_video = SavedVideo.objects.get(
                    user=request.user, video_id=video_id
                )
                notes = serializer.validated_data.get("notes")
                if notes:
                    saved_video.notes = notes
                    saved_video.save(update_fields=["notes"])
                logger.info(
                    f"Video {video_id} already saved by user {request.user.username}, updating notes"
                )

                # Return the existing saved video
                saved_serializer = SavedVideoSerializer(saved_video)
                return Response(saved_serializer.data, status=status.HTTP_200_OK)
            else:
                # Save new video
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )
        except Exception as e:
            logger.error(f"Error in create method: {str(e)}")
            return Response(
                {"error": f"Failed to save video: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def my_saved_videos(self, request):
        """Get all videos saved by the current user"""
        try:
            queryset = self.get_queryset()
            logger.info(f"Retrieving saved videos for user {request.user.username}")
            serializer = SavedVideoSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(
                f"Error retrieving saved videos for user {request.user.username}: {str(e)}"
            )
            return Response(
                {"error": "Failed to retrieve saved videos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
