from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
import json
import requests
import uuid
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from .models import User
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings

logger = logging.getLogger(__name__)


# Add a function to get tokens for user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@csrf_exempt
@require_POST
def register(request):
    try:
        # Try to parse JSON data first
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        # Fall back to form data if JSON parsing fails
        data = request.POST

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    nickname = data.get("nickname")
    age = data.get("age")
    gender = data.get("gender")

    # Basic validation
    if not username or not email or not password or not nickname:
        return JsonResponse(
            {"error": "Missing required fields (username, email, password, nickname)"},
            status=400,
        )

    # Check if username or email already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    if User.objects.filter(nickname=nickname).exists():
        return JsonResponse({"error": "Nickname already exists"}, status=400)

    # Create user
    user = User(
        username=username,
        email=email,
        password=make_password(password),
        nickname=nickname,
        age=age,
        gender=gender,
    )

    user.save()

    # Auto login after registration
    login(request, user)

    # Generate tokens
    tokens = get_tokens_for_user(user)

    return JsonResponse(
        {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "age": user.age,
                "gender": user.gender,
            },
            "tokens": tokens,
        },
        status=201,
    )


@csrf_exempt
@require_POST
def login_view(request):
    try:
        # Try to parse JSON data first
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        # Fall back to form data if JSON parsing fails
        data = request.POST

    username = data.get("username")
    password = data.get("password")

    # Try authenticating with username
    user = authenticate(request, username=username, password=password)

    # If authentication with username fails, try with email
    if user is None and "@" in username:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user is not None:
        login(request, user)

        # Generate tokens
        tokens = get_tokens_for_user(user)

        # Prepare user data for response
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "profile_img": (
                user.profile_img.url if user.profile_img else user.social_avatar
            ),
            "age": user.age,
            "gender": user.gender,
            "money": user.money,
            "salary": user.salary,
            "is_superuser": user.is_superuser,
        }

        return JsonResponse(
            {"message": "Login successful", "user": user_data, "tokens": tokens},
            status=200,
        )
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


@csrf_exempt
@require_POST
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    logout(request)
    return JsonResponse({"message": "Logout successful"}, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    logger.info(f"Update profile request for user: {user.username}")

    # Log request type and content
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"Request has FILES: {hasattr(request, 'FILES')}")
    if hasattr(request, "FILES"):
        logger.info(f"FILES keys: {request.FILES.keys()}")

    # For multipart/form-data, data comes from request.POST and request.FILES
    # For JSON, data is parsed automatically by DRF in request.data
    data = request.data
    print("data: ", data)

    # Get values from request.data
    nickname = data.get("nickname")
    age = data.get("age")
    gender = data.get("gender")
    salary = data.get("salary")
    money = data.get("money")

    # Handle image file upload
    image = request.FILES.get("profile_img") if hasattr(request, "FILES") else None
    logger.info(f"Received profile image: {image}")
    if image:
        logger.info(
            f"Image details - Name: {image.name}, Size: {image.size}, Content Type: {image.content_type}"
        )

    # Update nickname if provided and not taken
    if nickname and nickname != user.nickname:
        if User.objects.filter(nickname=nickname).exists():
            logger.warning(f"Nickname '{nickname}' already exists")
            return JsonResponse({"error": "Nickname already exists"}, status=400)
        logger.info(f"Updating nickname from '{user.nickname}' to '{nickname}'")
        user.nickname = nickname

    # Update other fields if provided
    if image:
        logger.info(f"Updating profile image to: {image}")
        try:
            if user.profile_img:
                # Delete old image if exists
                logger.info(f"Deleting old profile image: {user.profile_img}")
                try:
                    user.profile_img.delete(save=False)
                except Exception as e:
                    logger.error(f"Error deleting old profile image: {e}")
            user.profile_img = image
            logger.info(f"New profile image path: {user.profile_img}")
        except Exception as e:
            logger.error(f"Error setting profile image: {e}")
            return JsonResponse(
                {"error": f"Failed to update profile image: {str(e)}"}, status=500
            )

    if age != "":
        user.age = age

    if gender != "":
        user.gender = gender

    if salary != "":
        user.salary = salary

    if money != "":
        try:
            # Convert to integer to ensure it's a valid amount
            money_amount = int(money)
            user.money = money_amount
            logger.info(f"Updated money for user {user.username} to {money_amount}")
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid money value: {money}, error: {e}")
            return JsonResponse({"error": "Invalid money value provided"}, status=400)

    try:
        user.save()
        logger.info(f"User profile updated successfully: {user.username}")
    except Exception as e:
        logger.error(f"Error saving user profile: {e}")
        return JsonResponse(
            {"error": f"Failed to save profile: {str(e)}"}, status=500
        )  # Return updated user profile
    if user.profile_img:
        # Make sure we're returning a full URL, not a relative path
        profile_img_url = request.build_absolute_uri(user.profile_img.url)
    else:
        profile_img_url = user.social_avatar

    logger.info(f"Returning profile_img_url: {profile_img_url}")

    return JsonResponse(
        {
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "profile_img": profile_img_url,
                "age": user.age,
                "gender": user.gender,
                "money": user.money,
                "salary": user.salary,
            },
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST", "GET"])
def google_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code")

            if not code:
                return JsonResponse(
                    {"error": "Google authorization code is required"}, status=400
                )  # Exchange the authorization code for tokens
            try:
                # Get the front-end origin from the request
                origin = request.META.get("HTTP_ORIGIN") or request.META.get(
                    "HTTP_REFERER", ""
                ).rstrip("/")
                if not origin:
                    # Fallback to the configured value
                    origin = "http://localhost:5173"  # Default Vue dev server

                # Construct the redirect URI dynamically to match frontend
                redirect_uri = f"{origin}/login/google/callback"

                # Exchange code for token
                token_url = "https://oauth2.googleapis.com/token"
                token_data = {
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }

                token_response = requests.post(token_url, data=token_data)

                if token_response.status_code != 200:
                    logger.error(f"Google token exchange failed: {token_response.text}")
                    return JsonResponse(
                        {"error": "Failed to exchange Google code for token"},
                        status=401,
                    )

                token_json = token_response.json()
                id_token = token_json.get("id_token")

                # Now verify the ID token
                google_response = requests.get(
                    f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}"
                )

                if google_response.status_code != 200:
                    return JsonResponse({"error": "Invalid Google token"}, status=401)

                google_data = google_response.json()

                # Extract user data from the token payload
                google_id = google_data["sub"]
                email = google_data.get("email")
                name = google_data.get("name", "")
                picture = google_data.get("picture", "")

            except Exception as e:
                logger.error(f"Google token verification error: {str(e)}")
                return JsonResponse(
                    {"error": "Failed to verify Google token"}, status=401
                )

            # Check if user exists
            try:
                user = User.objects.get(google_id=google_id)
                # Update user info if needed
                if picture and not user.profile_img:
                    user.social_avatar = picture
                    user.save()
            except User.DoesNotExist:
                # Check if email exists
                try:
                    user = User.objects.get(email=email)
                    # Link Google account to existing user
                    user.google_id = google_id
                    user.social_avatar = picture or user.social_avatar
                    user.save()
                except User.DoesNotExist:
                    # Create new user
                    username = f"google_{google_id}"
                    nickname = name or f"user_{uuid.uuid4().hex[:8]}"

                    # Ensure nickname is unique
                    base_nickname = nickname
                    counter = 1
                    while User.objects.filter(nickname=nickname).exists():
                        nickname = f"{base_nickname}_{counter}"
                        counter += 1

                    user = User.objects.create(
                        username=username,
                        email=email,
                        nickname=nickname,
                        google_id=google_id,
                        social_avatar=picture,
                        # Generate a random password as it won't be used
                        password=make_password(uuid.uuid4().hex),
                    )

            # Log in the user
            login(request, user)

            # Generate tokens
            tokens = get_tokens_for_user(user)

            return JsonResponse(
                {
                    "message": "Google login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "nickname": user.nickname,
                        "profile_img": (
                            user.profile_img.url
                            if user.profile_img
                            else user.social_avatar
                        ),
                        "age": user.age,
                        "gender": user.gender,
                    },
                    "tokens": tokens,
                }
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return JsonResponse(
                {"error": "Server error during Google login"}, status=500
            )

    # For GET requests, return info about Google login
    return JsonResponse(
        {
            "message": "Please use POST to login with Google",
            "endpoints": {"login": "/accounts/google/login/"},
        }
    )


@csrf_exempt
@require_http_methods(["POST", "GET"])
def kakao_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code")

            if not code:
                return JsonResponse(
                    {"error": "Kakao authorization code is required"}, status=400
                )  # Get access token from Kakao
            token_endpoint = "https://kauth.kakao.com/oauth/token"

            # Get the front-end origin from the request
            # This assumes the request includes an Origin or Referer header
            origin = request.META.get("HTTP_ORIGIN") or request.META.get(
                "HTTP_REFERER", ""
            ).rstrip("/")
            if not origin:
                # Fallback to the configured value if origin cannot be determined
                origin = "http://localhost:5173"  # Default Vue dev server

            # Construct the redirect URI dynamically to match what's used in the frontend
            redirect_uri = f"{origin}/login/kakao/callback"

            token_data = {
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "code": code,
            }

            token_headers = {
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
            }

            token_response = requests.post(
                token_endpoint, data=token_data, headers=token_headers
            )

            if token_response.status_code != 200:
                return JsonResponse(
                    {"error": "Failed to get Kakao access token"}, status=401
                )

            access_token = token_response.json().get("access_token")

            # Get user info from Kakao
            user_info_endpoint = "https://kapi.kakao.com/v2/user/me"
            user_info_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            }

            user_info_response = requests.post(
                user_info_endpoint, headers=user_info_headers
            )

            if user_info_response.status_code != 200:
                return JsonResponse(
                    {"error": "Failed to get Kakao user info"}, status=401
                )

            kakao_data = user_info_response.json()
            kakao_id = str(kakao_data["id"])
            kakao_account = kakao_data.get("kakao_account", {})
            email = kakao_account.get("email")

            profile = kakao_account.get("profile", {})
            nickname = profile.get("nickname")
            profile_image = profile.get("profile_image_url")

            # Check if user exists
            try:
                user = User.objects.get(kakao_id=kakao_id)
                # Update user info if needed
                if profile_image and not user.profile_img:
                    user.social_avatar = profile_image
                    user.save()
            except User.DoesNotExist:
                # Check if email exists
                if email:
                    try:
                        user = User.objects.get(email=email)
                        # Link Kakao account to existing user
                        user.kakao_id = kakao_id
                        user.social_avatar = profile_image or user.social_avatar
                        user.save()
                    except User.DoesNotExist:
                        # Create new user
                        username = f"kakao_{kakao_id}"

                        # Ensure nickname is unique
                        base_nickname = nickname or f"user_{uuid.uuid4().hex[:8]}"
                        counter = 1
                        nickname = base_nickname
                        while User.objects.filter(nickname=nickname).exists():
                            nickname = f"{base_nickname}_{counter}"
                            counter += 1

                        user = User.objects.create(
                            username=username,
                            email=email,
                            nickname=nickname,
                            kakao_id=kakao_id,
                            social_avatar=profile_image,
                            password=make_password(uuid.uuid4().hex),
                        )
                else:
                    # Kakao didn't provide email
                    username = f"kakao_{kakao_id}"

                    # Ensure nickname is unique
                    base_nickname = nickname or f"user_{uuid.uuid4().hex[:8]}"
                    counter = 1
                    nickname = base_nickname
                    while User.objects.filter(nickname=nickname).exists():
                        nickname = f"{base_nickname}_{counter}"
                        counter += 1

                    user = User.objects.create(
                        username=username,
                        nickname=nickname,
                        kakao_id=kakao_id,
                        social_avatar=profile_image,
                        password=make_password(uuid.uuid4().hex),
                    )

            # Log in the user
            login(request, user)

            # Generate tokens
            tokens = get_tokens_for_user(user)

            return JsonResponse(
                {
                    "message": "Kakao login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "nickname": user.nickname,
                        "profile_img": (
                            user.profile_img.url
                            if user.profile_img
                            else user.social_avatar
                        ),
                        "age": user.age,
                        "gender": user.gender,
                    },
                    "tokens": tokens,
                }
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Kakao login error: {str(e)}")
            return JsonResponse(
                {"error": "Server error during Kakao login"}, status=500
            )

    # For GET requests, return info about Kakao login
    return JsonResponse(
        {
            "message": "Please use POST to login with Kakao",
            "endpoints": {"login": "/accounts/kakao/login/"},
        }
    )


@csrf_exempt
@require_POST
def check_auth(request):
    if request.user.is_authenticated:
        user = request.user
        return JsonResponse(
            {
                "is_authenticated": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "nickname": user.nickname,
                    "profile_img": (
                        user.profile_img.url if user.profile_img else user.social_avatar
                    ),
                    "age": user.age,
                    "gender": user.gender,
                },
            }
        )
    else:
        return JsonResponse({"is_authenticated": False})


@csrf_exempt
@require_POST
def get_user_profile(request):
    """
    Get detailed profile information for the currently authenticated user
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    user = request.user

    # Build absolute URL for profile image
    if user.profile_img:
        profile_img_url = request.build_absolute_uri(user.profile_img.url)
    else:
        profile_img_url = user.social_avatar

    profile_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "profile_img": profile_img_url,
        "age": user.age,
        "gender": user.gender,
        "money": user.money,
        "salary": user.salary,
        "date_joined": user.date_joined,
        "join_date": user.join_date,
        "is_admin": user.is_admin,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "last_login": user.last_login,
        "is_social_account": bool(user.google_id or user.kakao_id),
    }

    return JsonResponse({"user": profile_data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_profile_image(request):
    """Reset a user's profile image back to default (empty)"""
    user = request.user
    logger.info(f"Resetting profile image for user: {user.username}")

    try:
        # Delete the current profile image if it exists
        if user.profile_img:
            logger.info(f"Deleting profile image: {user.profile_img}")
            try:
                user.profile_img.delete(save=False)
            except Exception as e:
                logger.error(f"Error deleting profile image: {e}")

        # Set profile_img to None
        user.profile_img = None
        user.save()

        logger.info(f"Profile image reset successfully for user: {user.username}")

        # Return the updated user profile
        return JsonResponse(
            {
                "message": "Profile image reset successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "nickname": user.nickname,
                    "profile_img": user.social_avatar,  # Fall back to social avatar or None
                    "age": user.age,
                    "gender": user.gender,
                    "money": user.money,
                    "salary": user.salary,
                },
            },
            status=200,
        )
    except Exception as e:
        logger.error(f"Error resetting profile image: {e}")
        return JsonResponse(
            {"error": f"Failed to reset profile image: {str(e)}"}, status=500
        )
