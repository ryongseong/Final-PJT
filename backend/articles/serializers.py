from rest_framework import serializers
from .models import Article, Comment
from accounts.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nickname", "profile_img", "social_avatar")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Handle profile_img or social_avatar for user display
        if data["profile_img"] is None:
            data["profile_img"] = data["social_avatar"]
        return data


class CommentSerializer(serializers.ModelSerializer):
    writer = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "writer", "content", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ArticleListSerializer(serializers.ModelSerializer):
    writer = UserSimpleSerializer(read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "writer",
            "title",
            "created_at",
            "comment_count",
            "likes_count",
            "is_liked",
        )

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return request.user in obj.likes.all()


class ArticleSerializer(serializers.ModelSerializer):
    writer = UserSimpleSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "writer",
            "title",
            "content",
            "created_at",
            "updated_at",
            "comments",
            "comment_count",
            "likes_count",
            "is_liked",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return request.user in obj.likes.all()
