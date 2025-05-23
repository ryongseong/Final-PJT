from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("reset-profile-image/", views.reset_profile_image, name="reset_profile_image"),
    path("profile/", views.get_user_profile, name="user_profile"),
    path("google/login/", views.google_login, name="google_login"),
    path("kakao/login/", views.kakao_login, name="kakao_login"),
    path("check-auth/", views.check_auth, name="check_auth"),
    # JWT token endpoints
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
