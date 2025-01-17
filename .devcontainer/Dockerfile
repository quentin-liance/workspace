FROM python:3.11-slim-bookworm

ENV APP_FOLDER=/app/workspace
ENV USER=qliance
ENV HOME=/app

WORKDIR $HOME

RUN apt-get update && apt-get install -y git curl gnupg locales && rm -rf /var/lib/apt/lists/*

# Générer les locales, en particulier fr_FR.UTF-8
RUN echo "fr_FR.UTF-8 UTF-8" >/etc/locale.gen && locale-gen
ENV LANG=fr_FR.UTF-8
ENV LANGUAGE=fr_FR:fr
ENV LC_ALL=fr_FR.UTF-8

# Création du user
RUN useradd -s /bin/bash -d $HOME $USER && chown -R $USER: $HOME
USER $USER

# Installation de poetry
RUN pip install --user poetry
ENV PATH=$HOME"/.local/bin:${PATH}"
RUN poetry config virtualenvs.in-project true

ENTRYPOINT []
