# Dockerfile

# pull official base image
FROM python:3.10.7-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \
    apt-get -y install gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir celery redis

# copy project
COPY . /usr/src/app/


RUN chmod +x ./docker-entrypoint.sh
CMD ["./docker-entrypoint.sh"]