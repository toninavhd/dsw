import pytest


@pytest.mark.django_db
def test_models_are_available_on_admin(admin_client):
    MODELS = ('tasks.Task',)

    for model in MODELS:
        url_model_path = model.replace('.', '/').lower()
        url = f'/admin/{url_model_path}/'
        response = admin_client.get(url)
        assert response.status_code == 200, f'El modelo <{model}> no está habilitado en el admin.'
