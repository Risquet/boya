from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'buoys', views.BuoyViewSet)
router.register(r'parameters', views.ParameterViewSet)
router.register(r'data', views.DataViewSet)

urlpatterns = [
    path("insertData/<int:buoy_id>/", views.insertDataView, name="insert-data"),
    path("data/csv/<int:buoy_id>/<int:parameter_id>/", views.exportDataView, name="retrieve-data-csv"),
    path("buoyParameters/<int:buoy_id>/", views.getBuoyParametersView, name="buoy-parameters"),
    path("data/<int:buoy_id>/<int:parameter_id>/", views.dataByBuoyAndParameterView, name="retrieve-data"),
    path("uploadStatus/<int:buoy_id>/", views.getUploadJobStatusView, name="job-status"),
    path("getDateRangeForParameters/", views.getDateRangeForParametersView, name="date-range"),
    path("user/", views.userView, name="user"),
    path("role/", views.userView, name="role"),
    path('', include(router.urls)),
]
