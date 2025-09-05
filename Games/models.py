from django.db import models


class Admins(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    from django.db import models

class Folder(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    materials = models.TextField(blank=True, null=True)
    number_of_players = models.CharField(max_length=50)  # e.g. "5-10 players"
    time = models.CharField(max_length=50)  # e.g. "30 minutes"
    video_link = models.URLField(blank=True, null=True)

    # Many-to-many: one game can be in multiple folders
    folders = models.ManyToManyField(Folder, related_name="games")

    def __str__(self):
        return self.name