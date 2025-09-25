# build and run containers
up:
	docker-compose up --build

# run migrations
migrate:
	docker-compose run web python manage.py migrate

# run tests
test:
	docker-compose run --rm web pytest tests/

# clear the database
flush:
	docker-compose run --rm web python manage.py flush --no-input

# create seed data
seed:
	docker-compose run --rm web python manage.py seed
