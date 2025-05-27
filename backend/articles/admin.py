from django.contrib import admin
from .models import Article, Comment


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "writer", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "writer", "content", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content",)
