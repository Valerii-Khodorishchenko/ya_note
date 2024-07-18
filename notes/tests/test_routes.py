from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Толстой')
        cls.another = User.objects.create(username='Простой')
        cls.slug = 'title'
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='title',
            author=cls.author,
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', False),
            ('users:login', False),
            ('users:logout', False),
            ('users:signup', False),
            ('notes:add', TestRoutes.another),
            ('notes:list', TestRoutes.another),
            ('notes:success', TestRoutes.another),
        )
        for name, user in urls:
            if user:
                self.client.force_login(user)
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_view_edit_and_delete(self):
        user_statuses = (
            (TestRoutes.author, HTTPStatus.OK),
            (TestRoutes.another, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete',):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(TestRoutes.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        ):
            with self.subTest(name=name):
                url = reverse(name, args=(TestRoutes.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        for name in (
            'notes:add',
            'notes:list',
            'notes:success',
        ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
