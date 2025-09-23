# sensor_app

This is a monorepo with a **Django backend (with Django Ninja)**, a **React frontend**, and a **Postgres database**, fully containerized with Docker.

## Folder Structure

sensor_app/
├── backend/ # Django backend
│ ├── Dockerfile
│ ├── requirements.txt
│ └── manage.py
├── frontend/ # React frontend
│ ├── Dockerfile
│ ├── package.json
│ └── src/
└── docker-compose.yml

## Build and start all containers

docker-compose up --build

## Run migrations

docker-compose run backend python manage.py migrate

## Run tests

...

## API overview

...