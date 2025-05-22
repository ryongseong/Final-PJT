from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from .models import Article, Comment
import json


# Create your tests here.
class ArticleAPITestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpassword1",
            nickname="테스트유저1",
        )

        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpassword2",
            nickname="테스트유저2",
        )

        # Create test articles
        self.article1 = Article.objects.create(
            writer=self.user1, title="Test Article 1", content="This is test article 1"
        )

        self.article2 = Article.objects.create(
            writer=self.user2, title="Test Article 2", content="This is test article 2"
        )

        # Create test comments
        self.comment1 = Comment.objects.create(
            article=self.article1, writer=self.user2, content="Comment on article 1"
        )

        self.comment2 = Comment.objects.create(
            article=self.article2, writer=self.user1, content="Comment on article 2"
        )

    def test_get_articles_list(self):
        url = reverse("article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_article_detail(self):
        url = reverse("article-detail", args=[self.article1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Article 1")
        self.assertEqual(len(response.data["comments"]), 1)

    def test_create_article_unauthenticated(self):
        url = reverse("article-list")
        data = {"title": "New Article", "content": "New article content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_article_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("article-list")
        data = {"title": "New Article", "content": "New article content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(Article.objects.get(id=3).title, "New Article")
        self.assertEqual(Article.objects.get(id=3).writer, self.user1)

    def test_update_article(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("article-detail", args=[self.article1.id])
        data = {
            "title": "Updated Article 1",
            "content": "Updated content for article 1",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, "Updated Article 1")
        self.assertEqual(self.article1.content, "Updated content for article 1")

    def test_update_article_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse("article-detail", args=[self.article1.id])
        data = {
            "title": "Updated Article 1",
            "content": "Updated content for article 1",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_article(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("article-detail", args=[self.article1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 1)

    def test_delete_article_unauthorized(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse("article-detail", args=[self.article1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.count(), 2)

    def test_add_comment(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("add_comment", args=[self.article2.id])
        data = {"content": "New comment on article 2"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Comment.objects.filter(article=self.article2).count(), 2)

    def test_update_comment(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("comment_detail", args=[self.comment2.id])
        data = {"content": "Updated comment on article 2"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment2.refresh_from_db()
        self.assertEqual(self.comment2.content, "Updated comment on article 2")

    def test_delete_comment(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("comment_detail", args=[self.comment2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 1)
