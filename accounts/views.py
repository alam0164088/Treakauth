from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import random
from .models import PasswordResetOTP, User
from .serializers import (
    UserSerializer,
    PasswordResetEmailSerializer,
    PasswordResetOTPSerializer,
    NotificationSerializer,
)

User = get_user_model()

# ---------------- OTP পাঠানো (Forget Password) ----------------
class PasswordResetEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        otp = f"{random.randint(100000, 999999)}"
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            subject="Your OTP for Password Reset",
            message=f"Your OTP is {otp}. It will expire in 10 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

# ---------------- OTP দিয়ে পাসওয়ার্ড রিসেট ----------------
class PasswordResetOTPConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by('-created_at').first()
        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        otp_obj.delete()  # OTP একবার ব্যবহার হলে মুছে দাও

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

# ---------------- Register ----------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_mail(
            subject="Welcome to TrekBot!",
            message=f"Hi {user.username}, welcome to TrekBot!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

# ---------------- Profile ----------------
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# ---------------- Logout ----------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"})
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

# ---------------- Notification Toggle ----------------
class NotificationToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = NotificationSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = NotificationSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
