ARG PYTHON_VERSION=3.11.0


FROM --platform=arm64 python:${PYTHON_VERSION}-slim as base
ARG POETRY_VERSION=1.4.2

RUN apt-get update && apt-get install -y libgeos-dev


RUN pip install --disable-pip-version-check --no-input poetry==${POETRY_VERSION}
COPY pyproject.toml poetry.lock ./

FROM base as development
ENV POETRY_VIRTUALENVS_CREATE=0 PYTHONUNBUFFERED=1 PYTHONFAULTHANDLER=1
RUN poetry install --no-interaction
WORKDIR /app
COPY . .
CMD ["python", "run.py", "--reload"]