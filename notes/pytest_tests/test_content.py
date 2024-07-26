import pytest
from django.urls import reverse


from notes.forms import NoteForm


# # В тесте используем фикстуру заметки
# # и фикстуру клиента с автором заметок.
# def test_note_in_list_for_author(note, author_client):
#     url = reverse('notes:list')
#     # Запрашиваем страницу со списком заметок:
#     response = author_client.get(url)
#     # Получаем список объектов из контекста:
#     object_list = response.context['object_list']
#     # Проверяем, что заметка находится в этом списке:
#     assert note in object_list


# # В этом тесте тоже используем фикстуру заметки,
# # но в качестве клиента используем not_author_client;
# # в этом клиенте авторизован не автор заметки,
# # так что заметка не должна быть ему видна.
# def test_note_not_in_list_for_another_user(note, not_author_client):
#     url = reverse('notes:list')
#     response = not_author_client.get(url)
#     object_list = response.context['object_list']
#     # Проверяем, что заметки нет в контексте страницы:
#     assert note not in object_list

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
    url = reverse('notes:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list


# def test_create_note_page_contains_form(author_client):
#     url = reverse('notes:add')
#     # запрашиваем страницу создания заметки:
#     response = author_client.get(url)
#     # Проверяем, есть ли объект form в словаре контекста:
#     assert 'form' in response.context
#     # Проверяем, что объект формы относится к нужному классу.
#     assert isinstance(response.context['form'], NoteForm)


# # В параметры теста передаём фикстуру slug_for_args и клиент с автором заметки:
# def test_edit_note_page_contains_form(slug_for_args, author_client):
#     url = reverse('notes:edit', args=slug_for_args)
#     # Запрашиваем страницу редактирования заметки:
#     response = author_client.get(url)
#     # Проверяем, есть ли объект form в словаре контекста:
#     assert 'form' in response.context
#     # Проверяем, что объект формы относится к нужному классу.
#     assert isinstance(response.context['form'], NoteForm)


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        # Для тестирования страницы редактирования заминтки нужен slug заметки.
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    """
    Проверяю, что на страницы создания и редактирования заметки передаются
    формы.
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)
