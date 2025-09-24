# build and run containers
up:
	docker-compose up --build

# run migrations
migrate:
	docker-compose run web python manage.py migrate

# run tests
test:
	docker-compose run --rm web pytest tests/

# create seed data (make seed)
# TODO