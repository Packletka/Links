from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django_user_agents.utils import get_user_agent
from django.contrib.auth.views import LogoutView
from .models import ShortLink, Click
from django.http import HttpResponse
from django.contrib import messages
from .forms import URLShortenForm
from django.conf import settings
from geoip2 import database
import os


def base_context(request):
    """Базовый контекст для всех страниц"""
    return {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated  # Явная передача статуса
    }


def home(request):
    short_url = None
    link: ShortLink | None = None  # Добавляем переменную для хранения объекта ссылки
    device_stats = {}  # Добавляем для статистики по устройствам
    form = URLShortenForm()

    if request.method == 'POST':
        form = URLShortenForm(request.POST)
        if form.is_valid():
            # Создаем или получаем существующую короткую ссылку
            link, created = ShortLink.objects.get_or_create(
                original_url=form.cleaned_data['original_url'],
                defaults={
                    'user': request.user if request.user.is_authenticated else None
                }
            )
            short_url = link.get_short_url(request)
            messages.success(request, 'Ссылка успешно сокращена!')

            # Собираем статистику по устройствам
            # noinspection PyUnresolvedReferences
            total = link.click_stats.count()  # Используем related_name 'click_stats'
            if total > 0:
                # noinspection PyUnresolvedReferences
                device_stats = {
                    'desktop': round(link.click_stats.filter(device_type='desktop').count() / total * 100),
                    'mobile': round(link.click_stats.filter(device_type='mobile').count() / total * 100),
                    'tablet': round(link.click_stats.filter(device_type='tablet').count() / total * 100),
                }

    return render(request, 'shortener/home.html', {
        'form': form,
        'short_url': short_url,
        'link': link,  # Передаем объект ссылки в шаблон
        'device_stats': device_stats  # Передаем статистику по устройствам
    })


@login_required
def my_links(request):
    context = base_context(request)
    return render(request, 'shortener/my_links.html', context)


def about(request):
    context = base_context(request)
    return render(request, 'shortener/about.html', context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'shortener/signup.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'shortener/profile.html', {'user': request.user})


class CustomLogoutView(LogoutView):
    @require_POST
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def redirect_original(request, short_code):
    link = get_object_or_404(ShortLink, short_code=short_code)

    # Проверка защиты (если включена в settings.py)
    if settings.CLICK_PROTECTION.get('ENABLE', False):
        from django.core.cache import cache
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'click_protection:{ip}'
        clicks = cache.get(cache_key, 0)

        if clicks >= settings.CLICK_PROTECTION.get('MAX_CLICKS', 5):
            return HttpResponse("Слишком много запросов", status=429)

        cache.set(cache_key, clicks + 1,
                  settings.CLICK_PROTECTION.get('TIME_WINDOW', 60))

    # Собираем данные о переходе
    user_agent = get_user_agent(request)

    # Создаем запись о переходе
    click = Click(
        short_link=link,
        referer=request.META.get('HTTP_REFERER'),
        user_agent=str(user_agent),
        ip_address=request.META.get('REMOTE_ADDR')
    )

    # Определяем страну по IP (необязательно)
    try:
        geoip_path = getattr(settings, 'GEOIP_PATH', None)
        if geoip_path:
            with database.Reader(os.path.join(geoip_path, 'GeoLite2-Country.mmdb')) as reader:
                response = reader.country(click.ip_address)
                click.country = response.country.name
    except Exception as e:
        print(f"GeoIP error: {e}")  # Для отладки

    click.save()

    return redirect(link.original_url)
