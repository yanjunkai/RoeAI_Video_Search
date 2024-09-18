from django.urls import path
from .views import UploadVideoView, SearchVideoView

urlpatterns = [
    path('upload/', UploadVideoView.as_view(), name='upload_video'),
    path('search/', SearchVideoView.as_view(), name='search_video'),
]
