from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import User, PasswordResetOTP, Notification, Vendor, Reward, CheckIn, RewardRedemption
from .serializers import (
    UserSerializer, PasswordResetEmailSerializer, PasswordResetOTPSerializer,
    NotificationSerializer, RewardSerializer, CheckInSerializer, RewardRedemptionSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

# Password Reset Email
class PasswordResetEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                otp = f"{random.randint(100000, 999999)}"
                PasswordResetOTP.objects.update_or_create(
                    user=user,
                    defaults={'otp': otp, 'created_at': timezone.now()}
                )
                send_mail(
                    subject="Your OTP for Password Reset",
                    message=f"Your OTP is {otp}. It will expire in 10 minutes.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                )
                return Response({
                    "status": "success",
                    "message": "OTP sent to your email."
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "error",
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Password Reset OTP Confirmation
class PasswordResetOTPConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            user = User.objects.filter(email=email).first()
            if user:
                otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by('-created_at').first()
                if otp_obj and not otp_obj.is_expired():
                    user.set_password(new_password)
                    user.save()
                    otp_obj.delete()
                    return Response({
                        "status": "success",
                        "message": "Password has been reset successfully."
                    }, status=status.HTTP_200_OK)
                return Response({
                    "status": "error",
                    "message": "Invalid or expired OTP."
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "status": "error",
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Register
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "User registered successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Profile
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            "status": "success",
            "message": "User profile retrieved successfully",
            "data": serializer.data
        })

# Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    "status": "success",
                    "message": "Logout successful"
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "error",
                "message": "Refresh token is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                "status": "error",
                "message": "Invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

# Notification Toggle
class NotificationToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = NotificationSerializer(request.user)
        return Response({
            "status": "success",
            "message": "Notification settings retrieved",
            "data": serializer.data
        })

    def post(self, request):
        serializer = NotificationSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Notification settings updated",
                "data": serializer.data
            })
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Notification Count
class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({
            "status": "success",
            "message": "Unread notification count retrieved",
            "data": {"unread_count": unread_count}
        })

# Vendor Dashboard
class VendorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "vendor":
            return Response({
                "status": "error",
                "message": "Only vendors can access this."
            }, status=status.HTTP_403_FORBIDDEN)
        try:
            vendor = Vendor.objects.get(owner=request.user)
            total_notifications = Notification.objects.filter(user=request.user).count()
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
            total_rewards = Reward.objects.filter(vendor=vendor).count()
            total_checkins = CheckIn.objects.filter(vendor=vendor).count()
            total_redemptions = RewardRedemption.objects.filter(reward__vendor=vendor).count()
            data = {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "total_rewards": total_rewards,
                "total_checkins": total_checkins,
                "total_redemptions": total_redemptions,
            }
            return Response({
                "status": "success",
                "message": "Vendor dashboard data retrieved",
                "data": data
            })
        except Vendor.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Vendor profile not found."
            }, status=status.HTTP_404_NOT_FOUND)

# Rewards
class RewardListCreateView(generics.ListCreateAPIView):
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reward.objects.filter(vendor__owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "Reward created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RewardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reward.objects.filter(vendor__owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "status": "success",
                "message": "Reward updated successfully",
                "data": serializer.data
            })
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": "Reward deleted successfully"
        }, status=status.HTTP_200_OK)

# CheckIns
class CheckInListCreateView(generics.ListCreateAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "vendor":
            try:
                vendor = Vendor.objects.get(owner=user)
                return CheckIn.objects.filter(vendor=vendor)
            except Vendor.DoesNotExist:
                return CheckIn.objects.none()
        return CheckIn.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['entry_time'] = timezone.now()
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "Check-in logged successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CheckInDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "vendor":
            try:
                vendor = Vendor.objects.get(owner=user)
                return CheckIn.objects.filter(vendor=vendor)
            except Vendor.DoesNotExist:
                return CheckIn.objects.none()
        return CheckIn.objects.filter(user=user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.exit_time:
            instance.exit_time = timezone.now()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "message": "Check-out logged successfully",
                "data": serializer.data
            })
        return Response({
            "status": "error",
            "message": "Check-out already logged"
        }, status=status.HTTP_400_BAD_REQUEST)

# Reward Redemptions
class RewardRedemptionListCreateView(generics.ListCreateAPIView):
    serializer_class = RewardRedemptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "vendor":
            try:
                vendor = Vendor.objects.get(owner=user)
                return RewardRedemption.objects.filter(reward__vendor=vendor)
            except Vendor.DoesNotExist:
                return RewardRedemption.objects.none()
        return RewardRedemption.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "Reward redeemed successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Validation errors",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RewardRedemptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RewardRedemptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "vendor":
            try:
                vendor = Vendor.objects.get(owner=user)
                return RewardRedemption.objects.filter(reward__vendor=vendor)
            except Vendor.DoesNotExist:
                return RewardRedemption.objects.none()
        return RewardRedemption.objects.filter(user=user)
    


class NotificationToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all notifications for the authenticated user
        notifications = Notification.objects.filter(user=request.user)
        
        # Serialize the queryset of Notification objects, not the User object
        # The `many=True` argument is crucial for serializing a list of objects
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            "status": "success",
            "message": "Notifications retrieved successfully",
            "data": serializer.data
        })