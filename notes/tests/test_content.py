from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import Note, NoteForm

User = get_user_model()


class TestAddEditPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Неавтор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.notes = Note.objects.create(title='Тестовая заметка', text='текст',
                                        author=cls.author, slug='slug')

    def test_note_in_list_for_author(self):
        """Проверяю, что заметка видна автору в списке заметок"""
        response = self.author_client.get(reverse('notes:list'))
        self.assertIn(self.notes, response.context['object_list'])

    def test_note_not_in_list_for_another_user(self):
        """Проверяю, что заметка не видна другому пользователю"""
        response = self.not_author_client.get(reverse('notes:list'))
        self.assertNotIn(self.notes, response.context['object_list'])

    def test_create_note_page_contains_form(self):
        """
        Проверяю, что На страницы создания и редактирования заметки 
        передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', [self.notes.slug]),
        )
        for name, args in urls:
            with self.subTest(name=name):
                response = self.author_client.get(
                    reverse(name) if args is None else reverse(name, args=args)
                )
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
