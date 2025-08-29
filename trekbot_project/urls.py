from django.contrib import admin
from django.urls import path, include
from .views import home 

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),  # এখানে accounts এর URL গুলো include হচ্ছে
]
