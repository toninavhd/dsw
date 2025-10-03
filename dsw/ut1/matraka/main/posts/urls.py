from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('<slug:post_slug>/', views.post_detail, name='post-detail'),
]
