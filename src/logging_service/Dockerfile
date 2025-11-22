FROM python:3.10-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY src/logging_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY log_proto/ /usr/src/app/log_proto
COPY src/ /usr/src/app/src

ENV PYTHONPATH=/usr/src/app

EXPOSE 50052

CMD ["python", "-m", "src.logging_service.server"]