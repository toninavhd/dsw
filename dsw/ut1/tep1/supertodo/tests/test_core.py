import pytest
from django.conf import settings
from django.db import IntegrityError
from model_bakery import baker
from tasks.models import Task


@pytest.mark.django_db
def test_required_apps_are_installed():
    PROPER_APPS = ('tasks', 'shared')

    custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django')]
    for app in PROPER_APPS:
        app_config = f'{app}.apps.{app.title()}Config'
        assert app_config in custom_apps, (
            f'La aplicación <{app}> no está "creada/instalada" en el proyecto.'
        )
    assert len(custom_apps) >= len(PROPER_APPS), (
        'El número de aplicaciones propias definidas en el proyecto no es correcto.'
    )


@pytest.mark.django_db
def test_task_model_has_proper_fields():
    PROPER_FIELDS = (
        'name',
        'slug',
        'description',
        'completed',
        'created_at',
        'updated_at',
    )
    for field in PROPER_FIELDS:
        assert getattr(Task, field) is not None, f'El campo <{field}> no está en el modelo Task.'


@pytest.mark.django_db(transaction=True)
def test_task_model_has_proper_unique_constraints(task: Task):
    with pytest.raises(IntegrityError):
        baker.make_recipe('tests.task', slug=task.slug)


@pytest.mark.django_db
def test_task_model_has_proper_default_values():
    task = baker.make(Task)
    assert task.description == ''
    assert task.completed is False
