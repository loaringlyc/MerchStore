docker run --rm -v ./:/app/ openapitools/openapi-generator-cli generate \
           -i /app/src/api_service/openapi.yaml \
           -g python-flask  \
           -o /app/src/api_service/out