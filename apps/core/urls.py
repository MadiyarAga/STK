from django.urls import path

from apps.core.views import HealthView, ReadyView

app_name = 'core'

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('ready', ReadyView.as_view(), name='ready'),
]
