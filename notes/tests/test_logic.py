from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Заголовок заметки',
            'text': 'Текст заметки',
            'slug': 'note_address'
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяю, что анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """
        Проверяю, что залогиненный пользователь может создать заметку.
        Проверяю, что поля заметки содержат корректную информацию.
        """
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_slug_specified(self):
        """Проверяю, что форма валидна, когда slug указан и уникален."""
        self.assertTrue(NoteForm(data=self.form_data).is_valid())

    def test_if_slug_not_specified_generated_from_title(self):
        """
        Проверяю, что форма валидна, если slug не указан.
        Если адрес не указан, он генерируется из title.
        """
        del self.form_data['slug']
        self.assertTrue(NoteForm(data=self.form_data).is_valid())
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.slug, 'zagolovok-zametki')

    def test_slug_not_unique_raises_validation_error(self):
        del self.form_data['slug']
        self.auth_client.post(self.url, data=self.form_data)
        self.assertFalse(NoteForm(data=self.form_data).is_valid())
        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'text'
    NEW_NOTE_TEXT = 'text1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='title',
            text=cls.NOTE_TEXT,
            slug='title-slug',
            author=cls.author
        )
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'new title',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'title-slug'}

    def test_author_can_delete_note(self):
        """Проверяю, что автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверяю, что пользователь не может удалить чужую заметку."""
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Проверяю, что редактировать заметку может только автор."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_author_user(self):
        """
        Проверяю, что другой пользователь не может редактировать заметку
        пользователя-автора
        """
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
