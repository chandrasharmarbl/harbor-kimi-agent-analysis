#!/bin/bash
set -e

# Required to move to the solution directory for ansible playbook and
# docker compose to work correctly.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd $SCRIPT_DIR

ansible-playbook ansible/install-docker.yml

docker rm -f app-postgres app-nestjs || true

docker compose up -d --build