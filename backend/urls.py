"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

admin.site.site_header = "Administración"
admin.site.site_title = "Administración del sitio"
admin.site.index_title = "Administración del sitio"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentification.urls")),
    path("api/", include("api.urls")),
    path("buoys/", views.buoys, name="buoys"),
    path("buoys/multi-charts/<int:buoy_id>/", views.multicharts, name="multicharts"),
    path("buoys/stacked-charts/<int:buoy_id>/", views.stackedcharts, name="stackedcharts"),
    path("buoys/<int:buoy_id>/", views.buoy, name="buoy"),
    path("", views.home, name="home"),
    path("map/", views.map, name="map"),
    path("login/", views.entrar, name="login"),
    path("register/", views.registrar, name="register"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path('forgot-password/', views.forgotPassword, name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', views.resetPassword, name='reset-password'),
    path('logout/', views.salir, name='logout'), 
    path("news", views.news, name="news")
]
