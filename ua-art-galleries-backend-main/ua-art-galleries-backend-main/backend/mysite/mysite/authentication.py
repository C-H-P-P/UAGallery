from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

import jwt


class MinimalJWTAuthentication(authentication.BaseAuthentication):
    """DRF authentication for a *minimal* JWT.

    Payload contains ONLY:
      - userId
      - exp

    Header:
      Authorization: Bearer <token>
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).decode("utf-8")
        if not auth:
            return None

        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        token = parts[1]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"require": ["exp", "userId"]},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("userId")
        if user_id is None:
            raise AuthenticationFailed("Invalid token payload")

        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, token)

    def authenticate_header(self, request):
        return f'Bearer realm="{self.www_authenticate_realm}"'


def build_minimal_jwt(user) -> str:
    """Create JWT with ONLY {userId, exp}."""
    lifetime = getattr(settings, "MINIMAL_JWT_ACCESS_LIFETIME", None)
    if lifetime is None:
        
        from datetime import timedelta

        lifetime = timedelta(minutes=60)

    exp_dt = timezone.now() + lifetime
    payload = {
        "userId": user.pk,
        "exp": int(exp_dt.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
