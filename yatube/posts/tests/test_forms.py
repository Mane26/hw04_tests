from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        super().setUpClass()
        """ Создаем запись в базе данных для проверки сушествующего slug."""
        cls.author = User.objects.create_user(
            username='Автор постов'
        )
        cls.group = Group.objects.create(
            title='Название',
            slug='address',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='текст',
        )
        """ Создаем форму, если нужна проверка атрибутов."""
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(
            username='lolka'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Подсчитаем количество записей в Post."""
        reverse_address_profile = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        reverse_address_create = reverse('posts:post_create')
        post_count = Post.objects.count()
        form_data = {
            'text': 'текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse_address_create,
            data=form_data,
            follow=True
        )
        # Убедимся, что запись в базе данных не создалась
        # сравним количество записей в Task до и после отправки формы
        self.assertRedirects(response, reverse_address_profile)
        self.assertEqual(
            Post.objects.count(),
            post_count + 1
        )
        # Проверяем, что создалась запись с заданнымb параметрами
        self.assertTrue(
            Post.objects.filter(
                text='текст',
                group=self.group.id
            ).exists()
        )

    def test_post_edit(self):
        """ Проверяем страницу редактирования записи
        и авторизованных пользователей."""
        post_id = self.post.text
        form_data = {
            'text': 'стих',
            'group': self.group.id
        }
        reverse_address_profile = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        reverse_address_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )
        response = self.authorized_client.post(
            reverse_address_edit,
            data=form_data,
            follow=True
        )
        self.assertEqual(post_id, 'текст')
        self.assertRedirects(response, reverse_address_profile)
