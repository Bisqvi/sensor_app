# sensor_app

This is a monorepo with a **Django backend (with Django Ninja)**, a **React frontend**, and a **Postgres database**, fully containerized with Docker.

## Build and start all containers

docker-compose up --build
OR
make up

## Run migrations

docker-compose run web python manage.py migrate
OR
make migrate

## Run tests

docker-compose run --rm web pytest tests/
OR
make test

## API overview

see Swagger docs at /api/docs
...