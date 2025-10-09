from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register_view, login_view, logout_view, profile_view

urlpatterns = [
    path('signup/', register_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
