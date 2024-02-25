FROM python:3.12-slim as build

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry \
    && poetry config virtualenvs.in-project true \
    && poetry install --only main


FROM gcr.io/distroless/python3

WORKDIR /app

COPY --from=build /app/.venv/lib/python3.12/site-packages /app/site-packages

ENV PYTHONPATH /app/site-packages

COPY main.py /app/main.py

ENTRYPOINT ["python", "main.py"]
