from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    ProfileView,
    LogoutView,
    NotificationToggleView,
    PasswordResetEmailView,
    PasswordResetOTPConfirmView,
    NotificationCountView,
    VendorDashboardView,
    RewardListCreateView,
    RewardDetailView,
    CheckInListCreateView,
    CheckInDetailView,
    RewardRedemptionListCreateView,
    RewardRedemptionDetailView,
)

app_name = "trekbot_api"  # Namespace for URL names to avoid conflicts

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),

    # Notifications
    path("notifications/toggle/", NotificationToggleView.as_view(), name="notification_toggle"),
    path("notifications/count/", NotificationCountView.as_view(), name="notification_count"),

    # Vendor Dashboard
    path("vendor/dashboard/", VendorDashboardView.as_view(), name="vendor_dashboard"),

    # Password Reset
    path("password-reset/", PasswordResetEmailView.as_view(), name="password_reset"),
    path("password-reset/confirm/", PasswordResetOTPConfirmView.as_view(), name="password_reset_confirm"),

    # Rewards
    path("rewards/", RewardListCreateView.as_view(), name="reward_list"),
    path("rewards/<int:pk>/", RewardDetailView.as_view(), name="reward_detail"),

    # CheckIns
    path("checkins/", CheckInListCreateView.as_view(), name="checkin_list"),
    path("checkins/<int:pk>/", CheckInDetailView.as_view(), name="checkin_detail"),

    # Reward Redemptions
    path("redemptions/", RewardRedemptionListCreateView.as_view(), name="redemption_list"),
    path("redemptions/<int:pk>/", RewardRedemptionDetailView.as_view(), name="redemption_detail"),
]