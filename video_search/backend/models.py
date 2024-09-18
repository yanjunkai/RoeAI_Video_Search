from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    detected_objects = models.JSONField(default=list, blank=True)  # Store detected objects as a list
