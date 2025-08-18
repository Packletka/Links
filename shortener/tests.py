from django.test import TestCase
from django.urls import reverse
from .models import ShortLink


class ClickCounterTest(TestCase):
    def test_click_counter(self):
        # Создаем тестовую ссылку
        link = ShortLink.objects.create(
            original_url="https://example.com",
            short_code="test123"
        )

        # Проверяем начальное состояние
        self.assertEqual(link.click_stats.count(), 0)

        # Симулируем переход
        response = self.client.get(
            reverse('redirect', kwargs={'short_code': 'test123'}),
            follow=False
        )

        # Проверяем редирект
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://example.com")

        # Проверяем счетчик
        self.assertEqual(link.click_stats.count(), 1)