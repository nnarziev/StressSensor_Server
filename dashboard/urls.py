from . import views
from django.urls import path
from django.conf.urls import url

urlpatterns = [
    path('<str:user_id>/', views.ema_per_person),
    url(r'^main/?', views.index),
    url(r'^csv/?', views.extract_features, {"exportCSV": True}, name="export"),
    url(r'^feature/?', views.feature_extract),
]
