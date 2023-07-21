FROM python:latest

RUN pip install --upgrade pip
RUN pip install pipenv

WORKDIR /deploy

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

COPY ./docker/startup/ ./startup/
RUN chmod a+x /deploy/startup/*

WORKDIR /app
COPY ./src/ /app