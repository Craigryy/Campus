# Use an official Python runtime based on Debian 10 "buster" as a parent image.
ARG PYTHON_VERSION=3.10-slim-buster
FROM python:$PYTHON_VERSION

# Add user that will be used in the container.
RUN useradd wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

ARG BUILD_ENV=dev
ARG POETRY_VERSION=1.6.1

ENV BUILD_ENV="$BUILD_ENV"
ENV PYTHON_VERSION="$PYTHON_VERSION"

LABEL vibes.distro.name=linux
LABEL vibes.distro.release=debian
LABEL vibes.image.name=vibes-web
LABEL vibes.build.env="$BUILD_ENV"
LABEL vibes.python.version="$PYTHON_VERSION"


# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Install the application server.
RUN pip install "gunicorn==20.0.4"

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# setting locales
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8


# Use /app folder as a directory where the source code is stored.
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi

# load project files
COPY . /app

# create user and add to docker group
RUN adduser --disabled-password --gecos '' vibes && \
    groupadd docker && \
    usermod -aG docker vibes

# grant newly created user permissions on essential files
RUN chown -R vibes:$(id -gn vibes) /app/

# change user to newly created user
USER vibes
