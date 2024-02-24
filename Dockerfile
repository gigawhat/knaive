FROM python:3.12.1-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main

COPY main.py /app/main.py

CMD ["python", "main.py"]
