from django.db import models

class VideoGame(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    genre = models.CharField(max_length=100, null=False, blank=False)
    release_date = models.DateField(null=False, auto_now=True)
    developer = models.CharField(max_length=100, null=False, blank=False)
    publisher = models.CharField(max_length=100, null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
