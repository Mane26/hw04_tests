from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

POST_NUMBER = 10


def get_page(request, post_list):
    # Паджинация 10 постов на страницу
    paginator = Paginator(post_list, POST_NUMBER)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Функция index передает данные в шаблон index.html."""
    template = 'posts/index.html'
    post_list = Post.objects.all().select_related(
        'author',
        'group'
    ).order_by('-pub_date')
    page_obj = get_page(request, post_list)
    # Здесь код запроса к модели и создание словаря контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Функция group_posts передает данные в шаблон group_list.html."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related(
        'author'
    ).order_by('-pub_date')
    page_obj = get_page(request, post_list)
    # Здесь код запроса к модели и создание словаря контекста
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    """Здесь код запроса к модели и создание словаря контекста."""
    template = 'posts/profile.html'
    # В тело страницы выведен список постов
    author = get_object_or_404(
        User.objects.all().prefetch_related(
            'posts',
            'posts__group'
        ), username=username)
    posts_list = author.posts.all()
    page_obj = get_page(request, posts_list)
    # Здесь код запроса к модели и создание словаря контекста
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    """Здесь код запроса к модели и создание словаря контекста."""
    post = get_object_or_404(Post, pk=post_id)
    # В тело страницы выведен один пост, выбранный по pk
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Добавлена "Новая запись" для авторизованных пользователей."""
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', username=request.user.username)
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Добавлена страница редактирования записи."""
    # Права на редактирование должны быть только у автора этого поста
    # Остальные пользователи должны перенаправляться
    # На страницу просмотра поста
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    return render(request, template, {'is_edit': True, 'form': form})
