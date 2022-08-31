from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Автор постов')
        cls.group = Group.objects.create(
            title='Название',
            slug='address',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_author = Client()
        self.auth_author.force_login(self.author)
        self.user = User.objects.create_user(
            username='Пользователь без постов'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_for_everyone(self):
        reverse_group = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        reverse_user = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        reverse_post = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        urls_list = [
            '/',
            reverse_group,
            reverse_user,
            reverse_post,
        ]
        for urls in urls_list:
            response = self.guest_client.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unezisting_urls(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_template_urls_for_everyone(self):
        reverse_group = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        reverse_user = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        reverse_post = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        urls_set = {
            '/': 'posts/index.html',
            reverse_group: 'posts/group_list.html',
            reverse_user: 'posts/profile.html',
            reverse_post: 'posts/post_detail.html',
        }
        for urls, template in urls_set.items():
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertTemplateUsed(response, template)

    def test_urls_for_author(self):
        reverse_post_for_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )
        urls_list = [
            reverse_post_for_edit,
        ]
        for urls in urls_list:
            response = self.auth_author.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_for_urls_author(self):
        reverse_post_for_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )
        urls_set = {
            reverse_post_for_edit: 'posts/create_post.html'
        }
        for urls, template in urls_set.items():
            with self.subTest(urls=urls):
                response = self.auth_author.get(urls)
                self.assertTemplateUsed(response, template)

    def test_urls_for_authorized_user(self):
        urls_list = [
            '/create/',
        ]
        for urls in urls_list:
            response = self.authorized_client.get(urls)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_for_urls_authorized_user(self):
        urls_set = {
            '/create/': 'posts/create_post.html'
        }
        for urls, template in urls_set.items():
            with self.subTest(urls=urls):
                response = self.authorized_client.get(urls)
                self.assertTemplateUsed(response, template)
