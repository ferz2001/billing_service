FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt requirements.txt

RUN python3 -m venv venv && \
    /opt/app/venv/bin/pip install --upgrade pip && \
    /opt/app/venv/bin/pip install -r requirements.txt

COPY ./src .

EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "-c", "source /opt/app/venv/bin/activate && alembic upgrade head && gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind $BILLING_API_APP_HOST:$BILLING_API_APP_PORT" ]
