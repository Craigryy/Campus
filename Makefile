.PHONY: run build down test coverage

run:
	sudo docker compose up

build:
	sudo docker compose build

down:
	sudo docker compose down

test:
	sudo docker compose run --rm app sh -c "coverage run --source='.' manage.py test && coverage report -m"

coverage:
	sudo docker compose run --rm app sh -c "coverage html"
	sudo docker cp $$(sudo docker compose ps -q app):/app/htmlcov ./
	xdg-open htmlcov/index.html
