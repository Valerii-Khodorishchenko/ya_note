from http import HTTPStatus

import pytest
from pytils.translit import slugify
from pytest_django.asserts import assertFormError, assertRedirects
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


def test_user_can_create_note(author_client, author, form_data):
    """Провуряю, что залогиненый пользователь может создать заметку."""
    response = author_client.post(reverse('notes:add'), data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    """Провуряю, что анонимный пользователь не может создать заметку."""
    url = reverse('notes:add')
    login_url = reverse('users:login')
    assertRedirects(
        client.post(url, data=form_data), f'{login_url}?next={url}'
    )
    assert Note.objects.count() == 0


def test_not_unique_slug(author_client, note, form_data):
    """Проверяю, что невозможно создать две заметки с одинаковым slug."""
    form_data['slug'] = note.slug
    assertFormError(
        author_client.post(reverse('notes:add'), data=form_data),
        'form',
        'slug',
        errors=(note.slug + WARNING)
    )
    assert Note.objects.count() == 1


def test_empty_slug(author_client, form_data):
    """
    Проверяю, что если при создании заметки не заполнен slug, то он формируется
    автоматически.
    """
    form_data.pop('slug')
    assertRedirects(
        author_client.post(reverse('notes:add'), data=form_data),
        reverse('notes:success'))
    assert Note.objects.count() == 1
    assert Note.objects.get().slug == slugify(form_data['title'])


def test_author_can_edit_note(author_client, form_data, note, slug_for_args):
    """Проверяю, что пользователь может редактировать свою заметку."""
    assertRedirects(
        author_client.post(
        reverse('notes:edit', args=slug_for_args), form_data
        ),
        reverse('notes:success')
    )
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def test_other_user_cant_edit_note(not_author_client, form_data, note,
                                   slug_for_args):
    """Проверяю, что пользователь не может редактировать чужую заметку."""
    response = not_author_client.post(
        reverse('notes:edit', args=slug_for_args),
        form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(id=note.id)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug


def test_author_can_delete_note(author_client, slug_for_args):
    """Проверяю, что пользователь может удалить свою заметку."""
    assertRedirects(
        author_client.post(reverse('notes:delete', args=slug_for_args)),
        reverse('notes:success'))
    assert Note.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, slug_for_args):
    """Проверяю, что пользователь не может удалить чужую заметку."""
    response = not_author_client.post(
        reverse('notes:delete', args=slug_for_args)
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
