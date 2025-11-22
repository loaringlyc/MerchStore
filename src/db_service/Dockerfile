FROM python:3.10-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY src/db_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY db_proto/ /usr/src/app/db_proto
COPY src/ /usr/src/app/src

ENV PYTHONPATH=/usr/src/app

EXPOSE 50051

CMD ["python", "-m", "src.db_service.server"]