PY_SENTINAL = .venv/sentinal
JS_SENTINAL = node_modules/sentinal
PIPFILE = Pipfile
export PIPENV_VENV_IN_PROJECT = true

$(PY_SENTINAL): $(PIPFILE)
	-rm -rf .venv
	pipenv sync 
	touch $@

$(JS_SENTINAL): package.json
	-rm -rf node_modules
	npm install
	touch $@

clean:
	-rm -rf .venv node_modules media/build

runserver: $(PY_SENTINAL)
	pipenv run ./manage.py runserver

migrate: $(PY_SENTINAL)
	pipenv run ./manage.py migrate --noinput

pre-deploy: $(PY_SENTINAL)
	pipenv run ./manage.py collectstatic --noinput --settings=decruck.settings.local
	pipenv run ./manage.py migrate --settings=decruck.settings.local

makemigrations: $(PY_SENTINAL)
	pipenv run ./manage.py makemigrations

superuser: $(PY_SENTINAL)
	pipenv run ./manage.py createsuperuser

shell: $(PY_SENTINAL)
	pipenv run ./manage.py shell_plus

bootstrap: $(PY_SENTINAL)
	pipenv run ./manage.py sync_page_translation_fields
	pipenv run ./manage.py update_translation_fields
	pipenv run ./manage.py bootstrap 
	pipenv run ./manage.py import_compositions ./data/decruck-catalog-temp.csv

update-index: $(PY_SENTINAL)
	pipenv run ./manage.py update_index 

test: $(PY_SENTINAL)
	pipenv run ./manage.py test

webpack: $(JS_SENTINAL)
	npm run dev 

webpack-prod: $(JS_SENTINAL)
	npm run build 

docker-image:
	docker build -t nbuonin/decruck:`git log -n 1 --pretty="%h"` .

docker-test:
	cd docker && docker-compose up --build --abort-on-container-exit

docker-push:
	docker push nbuonin/decruck:`git log -n 1 --pretty="%h"`

makemessages:
	pipenv run ./manage.py makemessages -l fr
.PHONY: makemessages

compilemessages:
	# First add gettext to your $PATH, check 'brew info gettext'
	pipenv run ./manage.py compilemessages -l fr
.PHONY: compilemessages


.PHONY: clean runserver migrate makemigrations superuser shell test scss docker-image docker-test docker-push update-index bootstrap
