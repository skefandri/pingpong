from django.db import models

class Tournament(models.Model):
    players = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
