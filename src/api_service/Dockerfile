FROM python:3.10-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY src/api_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY db_proto/ /usr/src/app/db_proto
COPY log_proto/ /usr/src/app/log_proto
COPY src/ /usr/src/app/src

ENV PYTHONPATH=/usr/src/app

EXPOSE 8080

CMD ["python", "-m", "src.api_service.openapi_server.out.openapi_server"]