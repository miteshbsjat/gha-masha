# Set the base image to use for subsequent instructions
FROM python:3.13-slim-bookworm AS builder

# Set the working directory inside the container
WORKDIR /app

RUN pip3 install --target=/app masha==0.0.2

COPY . /app

FROM python:3.13-slim-bookworm

COPY --from=builder /app /app

WORKDIR /app

ENV PYTHONPATH /app

ENTRYPOINT ["/app/entrypoint.py"]
