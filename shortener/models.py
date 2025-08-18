from django.db import models
from django.contrib.auth.models import User
import shortuuid

class ShortLink(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    clicks = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = shortuuid.ShortUUID().random(length=6)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_url} → {self.short_code}"