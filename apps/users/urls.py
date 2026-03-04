from django.urls import path
from .views import me, register
from rest_framework_simplejwt.views import TokenRefreshView
from .token_serializer import CustomTokenObtainPairView

urlpatterns = [
    path('register/', register, name='register'),
    path('me/', me, name='me'),

    # 🔐 JWT Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]