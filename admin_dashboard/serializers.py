from rest_framework import serializers
from accounts.models import User, Vendor

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'shop']

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_vendors = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    reward_redemptions = serializers.IntegerField()