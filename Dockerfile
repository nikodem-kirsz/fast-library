FROM python:3 AS app

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY src/ /app/

ENV APP_ENV APP
ENV LOG_LEVEL NONE

ENTRYPOINT python -m app