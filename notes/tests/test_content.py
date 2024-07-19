from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from notes.forms import Note, NoteForm

User = get_user_model()


class TestAddEditPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.notes = Note.objects.create(title='Тестовая заметка', text='текст',
                                        author=cls.author, slug='slug')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))

    def test_anonymous_client_has_no_form(self):
        for name in (TestAddEditPage.add_url, TestAddEditPage.edit_url):
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertNotIn('form', response)

    def test_authorized_client_has_form(self):
        self.client.force_login(TestAddEditPage.author)
        for name in (TestAddEditPage.add_url, TestAddEditPage.edit_url):
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

