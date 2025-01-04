FROM python:3.11-slim-bookworm

ENV APP_FOLDER=/app/workspace
ENV USER=qliance
ENV HOME=/app

WORKDIR $HOME

RUN apt-get update && apt-get install -y git curl gnupg locales && rm -rf /var/lib/apt/lists/*

# Création du user
RUN useradd -s /bin/bash -d $HOME $USER && chown -R $USER: $HOME
USER $USER

# Installation de poetry
RUN pip install --user poetry
ENV PATH=$HOME"/.local/bin:${PATH}"
RUN poetry config virtualenvs.in-project true

ENTRYPOINT []