from django.contrib import admin
from .models import YouTubeVideo, SavedVideo


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "channel_title", "published_at", "search_query")
    search_fields = ("title", "description", "channel_title", "search_query")
    list_filter = ("channel_title", "published_at")
    ordering = ("-published_at",)


@admin.register(SavedVideo)
class SavedVideoAdmin(admin.ModelAdmin):
    list_display = ("user", "get_video_title", "saved_at")
    search_fields = ("user__username", "video__title", "notes")
    list_filter = ("saved_at",)
    ordering = ("-saved_at",)

    def get_video_title(self, obj):
        return obj.video.title

    get_video_title.short_description = "Video Title"
