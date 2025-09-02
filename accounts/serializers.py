from rest_framework import serializers
from .models import User, Notification, Vendor, Reward, CheckIn, RewardRedemption
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.exceptions import ValidationError

class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("No user with this email exists.")
        return value

class PasswordResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        try:
            otp_obj = PasswordResetOTP.objects.get(user__email=email, otp=otp)
            if otp_obj.is_expired():
                raise ValidationError("OTP has expired.")
        except PasswordResetOTP.DoesNotExist:
            raise ValidationError("Invalid OTP.")
        return data

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.get(email=email)
        user.password = make_password(validated_data['new_password'])
        user.save()
        PasswordResetOTP.objects.filter(user=user).delete()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "receive_notifications"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
    

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "message", "is_read", "created_at"]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = "__all__"

    def validate_valid_until(self, value):
        if value < timezone.now():
            raise ValidationError("Valid until date cannot be in the past.")
        return value

class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = "__all__"

    def validate(self, data):
        if data.get('exit_time') and data['exit_time'] < data['entry_time']:
            raise ValidationError("Exit time cannot be earlier than entry time.")
        return data

class RewardRedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardRedemption
        fields = "__all__"

    def validate(self, data):
        reward = data.get('reward')
        if reward.valid_until < timezone.now():
            raise ValidationError("Reward has expired.")
        redemptions_today = RewardRedemption.objects.filter(reward=reward, redeemed_at__date=timezone.now().date()).count()
        if redemptions_today >= reward.max_redemptions_per_day:
            raise ValidationError("Daily redemption limit exceeded.")
        return data