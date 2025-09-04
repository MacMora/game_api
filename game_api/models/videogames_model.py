from django.db import models

class VideoGame(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    release_date = models.DateField()
    developer = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    price = models.IntegerField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
