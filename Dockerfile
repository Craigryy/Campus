# # Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
# FROM python:3.12-slim-bookworm

# # Add user that will be used in the container.
# RUN useradd wagtail

# # Port used by this container to serve HTTP.
# EXPOSE 8000

# # Set environment variables.
# # 1. Force Python stdout and stderr streams to be unbuffered.
# # 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
# #    command.
# ENV PYTHONUNBUFFERED=1 \
#     PORT=8000

# # Install system packages required by Wagtail and Django.
# RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     libmariadb-dev \
#     libjpeg62-turbo-dev \
#     zlib1g-dev \
#     libwebp-dev \
#  && rm -rf /var/lib/apt/lists/*

# # Install the application server.
# RUN pip install "gunicorn==20.0.4"

# # Install the project requirements.
# COPY requirements.txt /
# RUN pip install -r /requirements.txt

# # Use /app folder as a directory where the source code is stored.
# WORKDIR /app

# # Set this directory to be owned by the "wagtail" user. This Wagtail project
# # uses SQLite, the folder needs to be owned by the user that
# # will be writing to the database file.
# RUN chown wagtail:wagtail /app

# # Copy the source code of the project into the container.
# COPY --chown=wagtail:wagtail . .

# # Use user "wagtail" to run the build commands below and the server itself.
# USER wagtail

# # Collect static files.
# RUN python manage.py collectstatic --noinput --clear

# # Runtime command that executes when "docker run" is called, it does the
# # following:
# #   1. Migrate the database.
# #   2. Start the application server.
# # WARNING:
# #   Migrating database at the same time as starting the server IS NOT THE BEST
# #   PRACTICE. The database should be migrated manually or using the release
# #   phase facilities of your hosting platform. This is used only so the
# #   Wagtail instance can be started with a simple "docker run" command.
# CMD set -xe; python manage.py migrate --noinput; gunicorn delsu.wsgi:application



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

LABEL script.distro.name=linux
LABEL script.distro.release=debian
LABEL script.image.name=script-web
LABEL script.build.env="$BUILD_ENV"
LABEL script.python.version="$PYTHON_VERSION"


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
RUN adduser --disabled-password --gecos '' script && \
    groupadd docker && \
    usermod -aG docker script

# grant newly created user permissions on essential files
RUN chown -R script:$(id -gn script) /app/

# change user to newly created user
USER script
