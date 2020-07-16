FROM python:3.7-slim
LABEL maintainer="nick@buonincontri.org"

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1
EXPOSE 8000

RUN apt-get update && apt-get install poppler-utils -y
RUN apt-get install libglib2.0-0 -y
RUN pip3 install pipenv
COPY . /app/
WORKDIR /app/

RUN set -ex && \
    pipenv sync && \
    useradd wagtail && \
    chown -R wagtail /app

USER wagtail

CMD pipenv run ./manage.py collectstatic --noinput --settings=decruck.settings.production && \
    pipenv run ./manage.py migrate --noinput && \
	pipenv run ./manage.py sync_page_translation_fields && \
	pipenv run ./manage.py update_translation_fields && \
    pipenv run gunicorn --bind 0.0.0.0:8000 --workers 1 --forwarded-allow-ips="*" decruck.wsgi:application
