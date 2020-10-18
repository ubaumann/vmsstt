ARG PYTHON
FROM python:3.9

WORKDIR /code
ENV PATH="/root/.poetry/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install tesseract-ocr curl -y \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && poetry config virtualenvs.create false

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-dev --no-interaction --no-ansi

COPY vmsstt vmsstt

EXPOSE 5000/tcp

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "vmsstt.flask_app:app"]