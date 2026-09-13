from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import CustomerRegisterView, CustomerProfileView, LogoutView

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', CustomerProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
]