import pytest
from django.urls import reverse

from notes.forms import NoteForm


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
def test_notes_list_for_different_users(note, parametrized_client,
                                        note_in_list):
    """
    Проверяю, что:
        -Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list в словаре context;
        -В список заметок одного пользователя не попадают заметки другого
        пользователя.
    """
    response = parametrized_client.get(reverse('notes:list'))
    assert (note in response.context['object_list']) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    """
    Проверяю, что на страницы создания и редактирования заметки передаются
    формы.
    """
    response = author_client.get(reverse(name, args=args))
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)
