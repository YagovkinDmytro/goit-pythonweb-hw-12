FROM python:3.11

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update && \
    apt-get install -y postgresql-client && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

COPY . .

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]