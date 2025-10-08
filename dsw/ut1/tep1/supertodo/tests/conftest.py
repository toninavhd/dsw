import pytest
from model_bakery import baker

from tasks.models import Task

TASK_LIST_URL = '/tasks/'
TASK_LIST_COMPLETED_URL = '/tasks/completed/'
TASK_LIST_PENDING_URL = '/tasks/pending/'
TASK_DETAIL_URL = '/tasks/{task_slug}/'
TASK_TOGGLE_URL = '/tasks/{task_slug}/toggle/'
TASK_EDIT_URL = '/tasks/{task_slug}/edit/'
TASK_DELETE_URL = '/tasks/{task_slug}/delete/'
TASK_ADD_URL = '/tasks/add/'


def get_url_and_tasks(completed: bool | None):
    match completed:
        case None:
            url = TASK_LIST_URL
            included_tasks = Task.objects.all()
            excluded_tasks = []
        case True:
            url = TASK_LIST_COMPLETED_URL
            included_tasks = Task.objects.filter(completed=True)
            excluded_tasks = Task.objects.filter(completed=False)
        case False:
            url = TASK_LIST_PENDING_URL
            included_tasks = Task.objects.filter(completed=False)
            excluded_tasks = Task.objects.filter(completed=True)
    return url, included_tasks, excluded_tasks


@pytest.fixture
def task():
    return baker.make_recipe('tests.task')
