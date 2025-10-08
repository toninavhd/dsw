import conftest
import pytest
from django.test import Client
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects

from tasks.models import Task

testdata = (
    (conftest.TASK_LIST_URL, 'Todas las tareas'),
    (conftest.TASK_LIST_COMPLETED_URL, 'Tareas completadas'),
    (conftest.TASK_LIST_PENDING_URL, 'Tareas pendientes'),
)

# ==============================================================================
# TASK LIST
# ==============================================================================


@pytest.mark.parametrize('url, filter', testdata)
@pytest.mark.django_db
def test_task_list_page_contains_title(client: Client, url: str, filter: str):
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'SuperTODO')
    assertContains(response, filter)


@pytest.mark.parametrize('completed', (None, True, False))
@pytest.mark.django_db
def test_task_list_page_contains_task_names(client: Client, completed: bool):
    baker.make_recipe('tests.task', _quantity=10)
    url, included_tasks, excluded_tasks = conftest.get_url_and_tasks(completed)
    response = client.get(url)
    assert response.status_code == 200
    for task in included_tasks:
        assertContains(response, task.name)
    for task in excluded_tasks:
        assertNotContains(response, task.name)


@pytest.mark.parametrize('completed', (None, True, False))
@pytest.mark.django_db
def test_task_list_page_contains_task_links(client: Client, completed: bool):
    baker.make_recipe('tests.task', _quantity=10)
    url, included_tasks, excluded_tasks = conftest.get_url_and_tasks(completed)
    response = client.get(url)
    assert response.status_code == 200
    for task in included_tasks:
        assertContains(response, conftest.TASK_DETAIL_URL.format(task_slug=task.slug))
        assertContains(response, conftest.TASK_TOGGLE_URL.format(task_slug=task.slug))
        assertContains(response, conftest.TASK_EDIT_URL.format(task_slug=task.slug))
        assertContains(response, conftest.TASK_DELETE_URL.format(task_slug=task.slug))
    for task in excluded_tasks:
        assertNotContains(response, conftest.TASK_DETAIL_URL.format(task_slug=task.slug))
        assertNotContains(response, conftest.TASK_TOGGLE_URL.format(task_slug=task.slug))
        assertNotContains(response, conftest.TASK_EDIT_URL.format(task_slug=task.slug))
        assertNotContains(response, conftest.TASK_DELETE_URL.format(task_slug=task.slug))


@pytest.mark.parametrize('completed', (None, True, False))
@pytest.mark.django_db
def test_task_list_page_contains_proper_emojis(client: Client, completed: bool):
    baker.make_recipe('tests.task', _quantity=10)
    url, included_tasks, excluded_tasks = conftest.get_url_and_tasks(completed)
    response = client.get(url)
    assert response.status_code == 200
    expected_check_emojis = included_tasks.filter(completed=True).count()
    expected_cross_emojis = included_tasks.filter(completed=False).count()
    rcontent = response.content.decode('utf-8')
    assert rcontent.count('✅') == expected_check_emojis
    assert rcontent.count('❌') == expected_cross_emojis


@pytest.mark.parametrize(
    'url',
    (conftest.TASK_LIST_URL, conftest.TASK_LIST_COMPLETED_URL, conftest.TASK_LIST_PENDING_URL),
)
@pytest.mark.django_db
def test_task_list_page_contains_filter_links(client: Client, url: str):
    baker.make_recipe('tests.task', _quantity=10)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, conftest.TASK_LIST_URL)
    assertContains(response, conftest.TASK_LIST_COMPLETED_URL)
    assertContains(response, conftest.TASK_LIST_PENDING_URL)


@pytest.mark.parametrize(
    'url',
    (conftest.TASK_LIST_URL, conftest.TASK_LIST_COMPLETED_URL, conftest.TASK_LIST_PENDING_URL),
)
@pytest.mark.django_db
def test_task_list_page_contains_add_task_link(client: Client, url: str):
    baker.make_recipe('tests.task', _quantity=10)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, conftest.TASK_ADD_URL)


@pytest.mark.parametrize(
    'url',
    (conftest.TASK_LIST_URL, conftest.TASK_LIST_COMPLETED_URL, conftest.TASK_LIST_PENDING_URL),
)
@pytest.mark.django_db
def test_task_list_page_no_tasks_message(client: Client, url: str):
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'Nada que hacer. ¡Enhorabuena!')


# ==============================================================================
# ADD TASK
# ==============================================================================


def test_add_task_page_contains_title(client: Client):
    response = client.get(conftest.TASK_ADD_URL)
    assert response.status_code == 200
    assertContains(response, 'SuperTODO')
    assertContains(response, 'Añadir tarea')


def test_add_task_page_contains_form(client: Client):
    response = client.get(conftest.TASK_ADD_URL)
    assert response.status_code == 200
    assertContains(response, '<form')
    assertContains(response, 'name="name"')
    assertContains(response, 'name="description"')
    assertContains(response, 'type="submit"')


@pytest.mark.django_db
def test_add_task_fails_when_no_name_provided(client: Client):
    response = client.post(conftest.TASK_ADD_URL, data={'description': 'A description'})
    assert response.status_code == 200
    assertContains(response, '<form')
    assertContains(response, 'name="name"')
    assertContains(response, 'name="description"')
    assertContains(response, 'type="submit"')
    assert Task.objects.count() == 0


@pytest.mark.django_db
def test_add_task_succeeds(client: Client):
    response = client.post(
        conftest.TASK_ADD_URL,
        data={'name': 'A task name', 'description': 'A description'},
        follow=True,
    )
    assertRedirects(response, conftest.TASK_LIST_URL)
    assert Task.objects.count() == 1
    task = Task.objects.first()
    assert task.name == 'A task name'
    assert task.slug == 'a-task-name'
    assert task.description == 'A description'
    assert not task.completed


@pytest.mark.django_db
def test_add_task_page_contains_cancel_link(client: Client):
    response = client.get(conftest.TASK_ADD_URL)
    assert response.status_code == 200
    assertContains(response, conftest.TASK_LIST_URL)


# ==============================================================================
# TASK DETAIL
# ==============================================================================


@pytest.mark.django_db
def test_task_detail_page_contains_title(client: Client, task: Task):
    url = conftest.TASK_DETAIL_URL.format(task_slug=task.slug)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'SuperTODO')


@pytest.mark.django_db
def test_task_detail_page_contains_required_task_info(client: Client):
    for completed in (True, False):
        task = baker.make_recipe('tests.task', completed=completed)
        url = conftest.TASK_DETAIL_URL.format(task_slug=task.slug)
        response = client.get(url)
        assert response.status_code == 200
        assertContains(response, task.name)
        assertContains(response, task.description)
        assertContains(response, 'Completada' if task.completed else 'Pendiente')


@pytest.mark.django_db
def test_task_detail_page_contains_back_link(client: Client, task: Task):
    url = conftest.TASK_DETAIL_URL.format(task_slug=task.slug)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, conftest.TASK_LIST_URL)


# ==============================================================================
# EDIT TASK
# ==============================================================================


@pytest.mark.django_db
def test_edit_task_page_contains_title(client: Client, task: Task):
    url = conftest.TASK_EDIT_URL.format(task_slug=task.slug)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'SuperTODO')
    assertContains(response, 'Editar tarea')


@pytest.mark.django_db
def test_edit_task_page_contains_cancel_link(client: Client, task: Task):
    url = conftest.TASK_EDIT_URL.format(task_slug=task.slug)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, conftest.TASK_LIST_URL)


@pytest.mark.django_db
def test_edit_task_page_contains_form_with_task_data(client: Client, task: Task):
    url = conftest.TASK_EDIT_URL.format(task_slug=task.slug)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, '<form')
    assertContains(response, 'name="name"')
    assertContains(response, f'value="{task.name}"')
    assertContains(response, 'name="description"')
    assertContains(response, f'>{task.description}</textarea>')
    assertContains(response, 'type="submit"')


@pytest.mark.django_db
def test_edit_task_succeeds(client: Client, task: Task):
    url = conftest.TASK_EDIT_URL.format(task_slug=task.slug)
    new_name = 'A new task name'
    new_description = 'A new description'
    response = client.post(
        url,
        data={'name': new_name, 'description': new_description},
        follow=True,
    )
    assertRedirects(response, conftest.TASK_DETAIL_URL.format(task_slug='a-new-task-name'))
    assertContains(response, new_name)
    assertContains(response, new_description)
    task.refresh_from_db()
    assert task.name == new_name
    assert task.slug == 'a-new-task-name'
    assert task.description == new_description


# ==============================================================================
# DELETE TASK
# ==============================================================================


@pytest.mark.django_db
def test_delete_task_succeeds(client: Client, task: Task):
    url = conftest.TASK_DELETE_URL.format(task_slug=task.slug)
    response = client.get(url)
    assertRedirects(response, conftest.TASK_LIST_URL)
    assert Task.objects.count() == 0


# ==============================================================================
# TOGGLE TASK
# ==============================================================================


@pytest.mark.django_db
def test_toggle_task_succeeds(client: Client, task: Task):
    task_status_before_toggle = task.completed
    url = conftest.TASK_TOGGLE_URL.format(task_slug=task.slug)
    response = client.get(url)
    assertRedirects(response, conftest.TASK_LIST_URL)
    task.refresh_from_db()
    assert task.completed is not task_status_before_toggle
