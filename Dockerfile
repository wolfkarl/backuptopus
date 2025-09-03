FROM python:3.11.2
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
RUN apt-get update && apt install postgresql-client -y && apt-get -y install cron

WORKDIR /app/backuptopus

COPY pyproject.toml .
COPY uv.lock .
RUN ls
RUN cat pyproject.toml
RUN uv sync 
RUN ls .venv

COPY . . 

# Run the command on container startup
CMD /bin/bash cron.sh


# ENTRYPOINT [ "uv", "run", "main.py" ]