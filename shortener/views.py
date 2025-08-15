from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Главная страница (форма сокращения ссылки)
def home(request):
    return render(request, 'shortener/home.html', {'user': request.user})

# Страница "Мои ссылки" (только для авторизованных)
@login_required
def my_links(request):
    return render(request, 'shortener/my_links.html', {'user': request.user})

# Страница "О проекте"
def about(request):
    return render(request, 'shortener/about.html', {'user': request.user})
