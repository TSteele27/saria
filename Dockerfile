FROM python:3.12.1

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
# RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./saria/__init__.py ./demo_app/__init__.py ./
RUN touch README.md
RUN /bin/true\
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && rm -rf /root/.cache/pypoetry
# RUN poetry install

COPY demo_app ./demo_app
COPY saria ./saria
COPY tests ./tests

RUN poetry install