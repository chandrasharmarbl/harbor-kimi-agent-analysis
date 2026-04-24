FROM ubuntu:24.04

# Install or copy over any environment dependencies here.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y ansible curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app