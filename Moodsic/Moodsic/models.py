from django.db import models
from django.contrib.auth.models import User

class Playlist(models.Model):
    title = models.CharField(max_length = 300)
    description = models.CharField(max_length = 1000)
    owner = models.CharField(max_length=300)
    link = models.CharField(max_length=300)
    image = models.CharField(max_length=300)

class Moodsic(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    playlist = models.ForeignKey(Playlist, on_delete= models.CASCADE, null = True, blank= True)
    mood = models.CharField(max_length = 30)
    typedText = models.CharField(max_length= 600)