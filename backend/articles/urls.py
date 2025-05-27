from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.ArticleViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("<int:article_id>/comments/", views.add_comment, name="add_comment"),
    path("comments/<int:comment_id>/", views.comment_detail, name="comment_detail"),
]
