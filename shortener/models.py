from django.db import models
from django.contrib.auth.models import User
import shortuuid
from django.urls import reverse


class ShortLink(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = shortuuid.ShortUUID().random(length=6)
        super().save(*args, **kwargs)

    def get_short_url(self, request):
        return request.build_absolute_uri(
            reverse('redirect', kwargs={'short_code': self.short_code}))

    def __str__(self):
        return f"{self.original_url} → {self.short_code}"

    @property
    def total_clicks(self):
        return self.click_stats.count()


class Click(models.Model):
    short_link = models.ForeignKey(ShortLink, related_name='click_stats', on_delete=models.CASCADE)
    click_timestamp = models.DateTimeField(auto_now_add=True)
    referer = models.URLField(max_length=2000, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        ua = self.user_agent or ''
        if 'Mobile' in ua:
            self.device_type = 'mobile'
        elif 'Tablet' in ua:
            self.device_type = 'tablet'
        else:
            self.device_type = 'desktop'
        super().save(*args, **kwargs)

    click_stats = models.Manager()

    @property
    def total_clicks(self):
        return self.click_stats.count()
