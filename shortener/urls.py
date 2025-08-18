from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .views import redirect_original
from .views import CustomLogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my-links/', views.my_links, name='my_links'),
    path('about/', views.about, name='about'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='shortener/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),

    # Оставляем ТОЛЬКО ОДИН из вариантов logout:
    path('logout/', CustomLogoutView.as_view(), name='logout'),  # Рекомендуемый вариант
    # ИЛИ (если не используете CustomLogoutView):
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Профиль
    path('accounts/profile/', login_required(views.profile), name='profile'),

    path('accounts/login/', auth_views.LoginView.as_view(
            template_name='shortener/login.html'
        ), name='login'),

    path('<str:short_code>/', redirect_original, name='redirect'),
]
