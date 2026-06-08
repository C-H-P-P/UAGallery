from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator               
from django.views.decorators.csrf import csrf_exempt               
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mysite.authentication import build_minimal_jwt


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name")


                                        
@method_decorator(csrf_exempt, name='dispatch')
class MinimalLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username") or request.data.get("login")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = build_minimal_jwt(user)
        return Response({"key": token}, status=status.HTTP_200_OK)


                                            
@method_decorator(csrf_exempt, name='dispatch')
class MinimalRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password") or request.data.get("password1")
        password2 = request.data.get("password2")

        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if not username or not password:
            return Response(
                {"detail": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password2 is not None and password != password2:
            return Response(
                {"detail": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "User with this username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = False
        user.save()

        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        import requests
        import os

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        verify_link = f"{frontend_url}/verify-email?uid={uid}&token={token}"
        
        brevo_api_key = os.environ.get("BREVO_API_KEY", "").strip()
        if brevo_api_key:
            payload = {
                "sender": {"name": "UA Gallery", "email": "uadbgallery@gmail.com"},
                "to": [{"email": user.email}],
                "subject": "Підтвердження реєстрації | UA Gallery",
                "htmlContent": f"Привіт, {user.first_name or username}!<br><br>Будь ласка, підтвердіть вашу електронну пошту, перейшовши за посиланням:<br><a href='{verify_link}'>{verify_link}</a><br><br>Якщо ви не реєструвалися на нашому сайті, просто проігноруйте цей лист."
            }
            try:
                res = requests.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=payload,
                    headers={"api-key": brevo_api_key, "Content-Type": "application/json"},
                    timeout=10
                )
                if res.status_code >= 400:
                    user.delete()
                    return Response({"detail": f"Помилка відправки листа (Brevo): {res.text}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                user.delete()
                return Response({"detail": f"Помилка сервера при відправці: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            user.delete()
            return Response({"detail": "BREVO_API_KEY не знайдено на сервері!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Registration successful. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
import os
import uuid
import jwt
from django.utils import timezone
from datetime import timedelta

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        google_id_token = request.data.get("google_id_token")
        if not google_id_token:
            return Response({"detail": "google_id_token is required"}, status=status.HTTP_400_BAD_REQUEST)

        client_id = os.environ.get("GOOGLE_CLIENT_ID") or getattr(settings, "GOOGLE_CLIENT_ID", None)

        try:
            idinfo = id_token.verify_oauth2_token(
                google_id_token,
                google_requests.Request(),
                client_id
            )
            email = idinfo.get("email")
            if not email:
                return Response({"detail": "Email not found in token"}, status=status.HTTP_400_BAD_REQUEST)

            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if not user:
                base_username = email.split('@')[0]
                username = base_username
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{uuid.uuid4().hex[:6]}"
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=idinfo.get("given_name", ""),
                    last_name=idinfo.get("family_name", "")
                )
                user.set_unusable_password()
                user.save()

            access_lifetime = getattr(settings, "MINIMAL_JWT_ACCESS_LIFETIME", timedelta(minutes=60))
            access_exp = int((timezone.now() + access_lifetime).timestamp())
            access_token = jwt.encode({"userId": user.pk, "exp": access_exp, "type": "access"}, settings.SECRET_KEY, algorithm="HS256")

            refresh_exp = int((timezone.now() + timedelta(days=7)).timestamp())
            refresh_token = jwt.encode({"userId": user.pk, "exp": refresh_exp, "type": "refresh"}, settings.SECRET_KEY, algorithm="HS256")

            return Response({
                "access": access_token,
                "refresh": refresh_token,
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"detail": f"Invalid Google token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

from django.utils.http import urlsafe_base64_decode

@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")

        if not uidb64 or not token:
            return Response({"detail": "uid and token are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            User = get_user_model()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        from django.contrib.auth.tokens import default_token_generator
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            from mysite.authentication import build_minimal_jwt
            jwt_token = build_minimal_jwt(user)

            return Response({
                "detail": "Email successfully verified. You are now logged in.",
                "key": jwt_token,
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid or expired verification token"}, status=status.HTTP_400_BAD_REQUEST)
