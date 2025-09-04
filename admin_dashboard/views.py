from rest_framework import generics
from rest_framework.response import Response
from django.utils import timezone
from accounts.models import User, Vendor, Reward, RewardRedemption
from .serializers import DashboardStatsSerializer, UserSerializer, VendorSerializer

class DashboardOverviewAPI(generics.GenericAPIView):
    serializer_class = DashboardStatsSerializer

    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        total_vendors = Vendor.objects.count()
        active_campaigns = Reward.objects.filter(valid_until__gte=timezone.now()).count()
        reward_redemptions = RewardRedemption.objects.count()

        users = User.objects.all()[:10]
        vendors = Vendor.objects.all()[:10]

        data = {
            'stats': {
                'total_users': total_users,
                'total_vendors': total_vendors,
                'active_campaigns': active_campaigns,
                'reward_redemptions': reward_redemptions,
            },
            'users': UserSerializer(users, many=True).data,
            'vendors': VendorSerializer(vendors, many=True).data,
        }
        return Response(data)