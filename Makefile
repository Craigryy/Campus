.PHONY: run build down test coverage

run:
	sudo docker compose run --rm app python manage.py makemigrations && sudo docker compose run --rm app python manage.py migrate && sudo docker compose up

build:
	sudo docker compose build

down:
	sudo docker compose down

test:
	sudo docker compose run --rm app sh -c "coverage run --source='.' manage.py test && coverage report -m"

coverage:
	sudo docker compose run --rm app sh -c "coverage html"
	xdg-open http://127.0.0.1:5500/htmlcov/index.html

lint:
	sudo docker compose run --rm app sh -c "flake8 && autopep8 --in-place --aggressive --aggressive -r ."

