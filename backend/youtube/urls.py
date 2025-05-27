from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import YouTubeViewSet, SavedVideoViewSet

router = DefaultRouter()
router.register(r"videos", YouTubeViewSet)
router.register(r"saved", SavedVideoViewSet, basename="saved")

urlpatterns = [
    path("", include(router.urls)),
]
