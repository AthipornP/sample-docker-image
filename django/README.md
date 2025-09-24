# Django Docker example

This folder contains a minimal example for running a Django application with Docker and PostgreSQL.

Files:
- `Dockerfile` - installs Python deps and runs Gunicorn.
- `docker-compose.yml` - defines `web` and `db` (Postgres) services.
- `requirements.txt` - minimal Python deps.

Quickstart:

1. Create a Django project (if you don't have one) in this folder, or mount your project into the image.

   django-admin startproject config .

2. Update `config/settings.py` DATABASES to use the `db` service host (`'HOST': 'db'`).

3. Build and run:

   docker compose up --build

4. Run migrations (in another terminal):

   docker compose run --rm web python manage.py migrate

Notes:
- For production, configure static files, collectstatic, and secure settings (SECRET_KEY, ALLOWED_HOSTS).
- Use a dedicated requirements file that pins versions for reproducible builds.
