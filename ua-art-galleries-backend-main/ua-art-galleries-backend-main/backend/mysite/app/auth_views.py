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

        token = build_minimal_jwt(user)
        return Response({"key": token}, status=status.HTTP_201_CREATED)


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
