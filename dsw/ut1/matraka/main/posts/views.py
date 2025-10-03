from django.http import HttpResponse
from django.shortcuts import render

from .models import Post


def post_list(request):
    posts = Post.objects.all()

    return render(request, 'posts/post/list.html', {'posts': posts})


def post_detail(request, post_slug: str):
    try:
        post = Post.objects.get(slug=post_slug)
    except Post.DoesNotExist:
        return HttpResponse(f'Post with slug "{post_slug}" does not exist!')
    return request('posts/post/detail.html', {'post': post})
