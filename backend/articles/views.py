from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging

from .models import Article, Comment
from .serializers import ArticleSerializer, ArticleListSerializer, CommentSerializer

logger = logging.getLogger(__name__)


# Create your views here.
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        return ArticleSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Make sure the request is in the context
        if not context.get("request") and hasattr(self, "request"):
            context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)

    def update(self, request, *args, **kwargs):
        article = self.get_object()
        # Check if the user is the writer of the article
        if article.writer != request.user:
            return Response(
                {"error": "You don't have permission to edit this article"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        article = self.get_object()
        # Check if the user is the writer of the article
        if article.writer != request.user:
            return Response(
                {"error": "You don't have permission to delete this article"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        article = self.get_object()
        user = request.user

        if article.likes.filter(id=user.id).exists():
            # User has already liked this article, so unlike it
            article.likes.remove(user)
            return Response({"status": "unliked"})
        else:
            # User hasn't liked this article yet, so like it
            article.likes.add(user)
            return Response({"status": "liked"})

    @action(detail=False, methods=["get"])
    def sort_by_likes(self, request):
        # Use annotate to count likes and order by that annotation
        articles = Article.objects.annotate(likes_count=Count("likes")).order_by(
            "-likes_count"
        )
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_comment(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(writer=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    # Check if the user is the writer of the comment
    if comment.writer != request.user:
        return Response(
            {"error": "You don't have permission to modify this comment"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PUT":
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        comment.delete()
        return Response(
            {"message": "Comment deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
