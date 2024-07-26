from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор")
        cls.another = User.objects.create(username="Другой пользователь")
        cls.slug = "title"
        cls.note = Note.objects.create(
            title="title",
            text="text",
            slug="title",
            author=cls.author,
        )

    def test_pages_availability(self):
        """
        Проверяю, что:
            - Главная страница доступна анонимному пользователю.
            - Аутентифицированному пользователю доступна страница со списком
            заметок notes/, страница успешного добавления заметки done/,
            страница добавления новой заметки add/.
            -Страницы регистрации пользователей, входа в учётную запись и
            выхода из неё доступны всем пользователям.
        """
        urls = (
            ("notes:home", None),
            ("users:login", None),
            ("users:logout", None),
            ("users:signup", None),
            ("notes:add", self.another),
            ("notes:list", self.another),
            ("notes:success", self.another),
        )
        for name, user in urls:
            with self.subTest(name=name):
                if user is not None:
                    self.client.force_login(user)
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_view_edit_and_delete(self):
        """
        Проверяю, что cтраницы отдельной заметки, удаления и редактирования
        заметки доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in (
                "notes:detail",
                "notes:edit",
                "notes:delete",
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяю, что при попытке перейти на страницу списка заметок, страницу
        успешного добавления записи, страницу добавления заметки, отдельной
        заметки, редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        urls = (
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
            ("notes:add", None),
            ("notes:list", None),
            ("notes:success", None),
        )
        login_url = reverse("users:login")
        for name, slug in urls:
            with self.subTest(name=name):
                url = reverse(name) if slug is None else reverse(name, args=slug)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
