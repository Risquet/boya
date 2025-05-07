from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views


urlpatterns = [
    path("login/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("user/", views.UserView.as_view(), name="user"),
    path("update/", views.UpdateUserView.as_view(), name="update"),
    path("update_password/", views.UpdatePasswordView.as_view(), name="update_password"),
]
