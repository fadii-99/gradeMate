import uuid
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  
    name = models.CharField(max_length=150, default=True)
    active_status = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    token_secret = models.CharField(max_length=64, default=uuid.uuid4().hex)  # used for token invalidation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
