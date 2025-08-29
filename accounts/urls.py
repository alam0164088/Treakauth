from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    ProfileView,
    LogoutView,
    NotificationToggleView,
    PasswordResetEmailView,
    PasswordResetOTPConfirmView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("notifications/", NotificationToggleView.as_view(), name="notification-toggle"),
    path("password-reset/", PasswordResetEmailView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetOTPConfirmView.as_view(), name="password-reset-confirm"),
]
