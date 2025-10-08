# Run development server
dev:
    uv run manage.py runserver

alias c:=check
# Check Django project
check:
    uv run manage.py check

# Setup project
setup: && migrate create-su set-tz
    #!/usr/bin/env bash
    uv sync
    uv run django-admin startproject main .

alias mm:=makemigrations
# Make model migrations
makemigrations app="":
    uv run manage.py makemigrations {{app}}

alias m:=migrate
# Apply model migrations
migrate app="":
    uv run manage.py migrate {{app}}

# Set Django TimeZone
set-tz timezone="Atlantic/Canary":
    #!/usr/bin/env bash
    sed -i -E "s@(TIME_ZONE).*@\1 = '{{ timezone }}'@" ./main/settings.py
    if [ $? -eq 0 ]; then
        echo "✔ Fixed TIME_ZONE='{{ timezone }}' and LANGUAGE_CODE='es-es'"
    fi

# Create a superuser (or update it if already exists)
create-su username="admin" password="admin" email="admin@example.com":
    #!/usr/bin/env bash
    uv run manage.py shell -c '
    from django.contrib.auth.models import User
    user, _ = User.objects.get_or_create(username="{{ username }}")
    user.email = "{{ email }}"
    user.set_password("{{ password }}") 
    user.is_superuser = True
    user.is_staff = True
    user.save()
    ' 
    echo "✔ Created superuser → {{ username }}:{{ password }}"

# Add a new app and install it on settings.py
startapp app:
    #!/usr/bin/env bash
    uv run manage.py startapp {{ app }}
    APP_CLASS={{ app }}
    APP_CONFIG="{{ app }}.apps.${APP_CLASS^}Config"
    perl -0pi -e "s/(INSTALLED_APPS *= *\[)(.*?)(\])/\1\2    '$APP_CONFIG',\n\3/smg" ./main/settings.py
    echo "✔ App '{{ app }}' created & added to settings.INSTALLED_APPS"

# Remove migrations and database. Reset DB artefacts.
[confirm("⚠️ All migrations and database will be removed. Continue? [yN]:")]
reset-db: && create-su
    #!/usr/bin/env bash
    find . -path "*/migrations/*.py" ! -path "./.venv/*" ! -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" ! -path "./.venv/*" -delete
    rm -f db.sqlite3
    ./manage.py makemigrations
    ./manage.py migrate
    echo

# Remove virtualenv
[confirm("⚠️ Virtualenv './venv' will be removed. Continue? [yN]:")]
rm-venv:
    rm -fr .venv

# Kill existent manage.py processes
kill:
    pkill -f "[Pp]ython.*manage.py runserver" || echo "No process"

# Clean data
[private]
clean-data:
    #!/usr/bin/env bash
    uv run manage.py shell -c '
    from tasks.models import Task

    Task.objects.all().delete()
    ' 

# Load fixtures into database
@load-data: clean-data
    uv run manage.py loaddata fixtures/tasks.json

# Launch tests
test pytest_args="":
    uv run pytest -s {{ pytest_args }}

alias sh:=shell
# Open project (django) shell
shell:
    uv run manage.py shell

alias dbsh:=dbshell
# Open database shell
dbshell:
    uv run manage.py dbshell
