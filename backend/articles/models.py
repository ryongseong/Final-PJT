from django.db import models
from accounts.models import User


# Create your models here.
class Article(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_articles", blank=True)

    def __str__(self):
        return self.title

    def likes_count(self):
        return self.likes.count()


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.writer.nickname} on {self.article.title}"
