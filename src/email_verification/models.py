from django.db import models


class Verification(models.Model):
    email = models.EmailField(max_length=100)
    connection_id = models.UUIDField()
    invite_url = models.URLField(max_length=2000)


class SessionState(models.Model):
    connection_id = models.UUIDField()
    state = models.TextField()
