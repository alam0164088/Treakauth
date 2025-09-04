from django.urls import path
from .views import DashboardOverviewAPI

urlpatterns = [
    path('dashboard/', DashboardOverviewAPI.as_view(), name='dashboard-overview-api'),
]