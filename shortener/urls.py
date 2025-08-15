from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my-links/', views.my_links, name='my_links'),
    path('about/', views.about, name='about'),
]
