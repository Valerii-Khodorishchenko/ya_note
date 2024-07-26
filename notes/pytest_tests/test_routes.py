from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


# # Указываем в фикстурах встроенный клиент.
# def test_home_availability_for_anonymous_user(client):
#     """
#     Проверяем, что анонимному пользователю доступна главная страница проекта
#     """
#     # Адрес страници получаем через reverse():
#     url = reverse('notes:home')
#     response = client.get(url)
#     assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'name',  # Имя параметра функции.
        # Значения, которые будут передоваться в name.
        ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    """
    Проверяем, что анонимному пользователю доступны 'notes:home',
    'users:login', 'users:logout', 'users:signup'
    """
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('notes:list', 'notes:add', 'notes:success'))
def test_pages_availability_for_auth_user(not_author_client, name):
    """
    Проверяем, что залогиненому пользователю доступны 'notes:list',
    'notes:add', 'notes:success'
    """
    url = reverse(name)
    # response = admin_client.get(url)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK

# Параметризуем тестирующую функцию:
# нужно передать фикстуры-клиенты и ожидаемый код ответа для каждого клиента.
@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'parametrized_client, expected_status',
    # В кортеже с кортежами передаём значения для параметров:
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize('name', ('notes:detail', 'notes:edit',
                                  'notes:delete'))
def test_pages_availability_for_author(parametrized_client, expected_status,
                                       name, note):
    """
    Проверяем, что автору заметок доступны 'note:detail', 'note:edit',
    'note:delete', другим возвращает ошибку 404
    """
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    # Во второй параметр передаём note_object,
    # в котором будет либо фикстура с объектом заметки, либо Note.
    # 'name, note_object',
    # (
    #     ('notes:detail', pytest.lazy_fixture('note')),
    #     ('notes:edit', pytest.lazy_fixture('note')),
    #     ('notes:delete', pytest.lazy_fixture('note')),
    #     ('notes:add', None),
    #     ('notes:success', None),
    #     ('notes:list', None),
    # ),
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
# def test_redirects(client, name, note_object):
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    
    # # Формируем URL в зависимости от того, передан ли объект заметки:
    # if note_object is not None:
    #     url = reverse(name, args=(note_object.slug,))
    # else:
    #     url = reverse(name)
    
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
