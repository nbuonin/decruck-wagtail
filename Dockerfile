FROM python:3.7-slim
LABEL maintainer="nick@buonincontri.org"

ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1
EXPOSE 8000

RUN apt-get update
RUN apt-get install libglib2.0-0 -y
RUN pip3 install pipenv
COPY . /app/
WORKDIR /app/

RUN set -ex && \
    pipenv sync && \
    useradd wagtail && \
    chown -R wagtail /app

USER wagtail

CMD pipenv run ./manage.py migrate && \
    pipenv run ./manage.py runserver 0.0.0.0:8000
