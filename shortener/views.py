from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from .forms import URLShortenForm
from .models import ShortLink


def base_context(request):
    """Базовый контекст для всех страниц"""
    return {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated  # Явная передача статуса
    }


def home(request):
    short_url = None
    form = URLShortenForm()

    if request.method == 'POST':
        form = URLShortenForm(request.POST)
        if form.is_valid():
            # Создаем или получаем существующую короткую ссылку
            link, created = ShortLink.objects.get_or_create(
                original_url=form.cleaned_data['original_url'],
                user=request.user if request.user.is_authenticated else None
            )
            short_url = link.get_short_url(request)
            messages.success(request, 'Ссылка успешно сокращена!')

    return render(request, 'shortener/home.html', {
        'form': form,
        'short_url': short_url
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
    link.clicks += 1
    link.save()
    return redirect(link.original_url)
