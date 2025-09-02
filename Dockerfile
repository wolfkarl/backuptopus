FROM python:3.11.2
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
RUN apt-get update && apt install postgresql-client -y

WORKDIR /app/pybackup

COPY pyproject.toml .
RUN uv sync

COPY . . 
ENTRYPOINT [ "uv", "run", "main.py" ]