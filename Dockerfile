FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache libpq

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]