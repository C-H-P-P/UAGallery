from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "is_active")


# 👇 МАГІЯ ТУТ: Вимикаємо CSRF для логіна
@method_decorator(csrf_exempt, name='dispatch')
class MinimalLoginView(APIView):
    permission_classes = [AllowAny]

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

        # Use Token instead of JWT
        token, created = Token.objects.get_or_create(user=user)
        return Response({"key": token.key}, status=status.HTTP_200_OK)


# 👇 МАГІЯ ТУТ: Вимикаємо CSRF для реєстрації
@method_decorator(csrf_exempt, name='dispatch')
class MinimalRegisterView(APIView):
    permission_classes = [AllowAny]

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
                {"detail": "User already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Use Token instead of JWT
        token = Token.objects.create(user=user)
        return Response({"key": token.key}, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        new_password_confirm = request.data.get("new_password_confirm")

        # Валідація: всі поля обов'язкові
        if not current_password or not new_password or not new_password_confirm:
            return Response(
                {"detail": "Всі поля обов'язкові для заповнення"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Валідація: перевірка поточного пароля
        if not request.user.check_password(current_password):
            return Response(
                {"detail": "Поточний пароль невірний"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Валідація: новий пароль має співпадати з підтвердженням
        if new_password != new_password_confirm:
            return Response(
                {"detail": "Нові паролі не співпадають"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Валідація: мінімальна довжина пароля
        if len(new_password) < 8:
            return Response(
                {"detail": "Пароль має містити мінімум 8 символів"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Валідація: новий пароль не може бути таким самим як поточний
        if current_password == new_password:
            return Response(
                {"detail": "Новий пароль має відрізнятися від поточного"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Зміна пароля (автоматично хешується)
        request.user.set_password(new_password)
        request.user.save()

        return Response(
            {"detail": "Пароль успішно змінено"},
            status=status.HTTP_200_OK,
        )