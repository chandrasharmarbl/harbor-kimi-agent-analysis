#!/bin/bash
set -e

cat << 'EOF' > install-docker.yml
---
- name: Install Docker
  hosts: localhost
  connection: local
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
    - name: Install docker and compose
      apt:
        name:
          - docker.io
          - docker-compose-v2
        state: present
EOF

ansible-playbook install-docker.yml

mkdir -p app-nestjs

cat << 'EOF' > app-nestjs/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(8080, '0.0.0.0');
}
bootstrap();
EOF

cat << 'EOF' > app-nestjs/app.controller.ts
import { Controller, Get, InternalServerErrorException } from '@nestjs/common';
import { Client } from 'pg';

@Controller()
export class AppController {
  @Get('checkdb')
  async checkDb() {
    const client = new Client({
      host: 'app-postgres',
      port: 5432,
      user: 'postgres',
      password: 'password',
      database: 'postgres',
    });
    try {
      await client.connect();
      const res = await client.query('SELECT 1 as result');
      await client.end();
      return { success: true, data: res.rows };
    } catch (err) {
      throw new InternalServerErrorException('Database connection failed: ' + err.message);
    }
  }
}
EOF

cat << 'EOF' > app-nestjs/Dockerfile
FROM node:20-alpine
WORKDIR /app

# Scaffold the app inside the Docker build process
RUN npx -y @nestjs/cli new nestjs-app --package-manager npm --skip-install

WORKDIR /app/nestjs-app
# Add the postgres client dependency
RUN npm install pg

# Overwrite the generated files with our custom logic
COPY main.ts src/main.ts
COPY app.controller.ts src/app.controller.ts

# Install all dependencies and build the app
RUN npm install
RUN npm run build

EXPOSE 8080
CMD ["npm", "run", "start:prod"]
EOF

cat << 'EOF' > docker-compose.yml
version: '3.8'
services:
  app-postgres:
    image: postgres:latest
    container_name: app-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 2s
      timeout: 2s
      retries: 5

  app-nestjs:
    build:
      context: ./app-nestjs
      dockerfile: Dockerfile
    container_name: app-nestjs
    ports:
      - "8080:8080"
    depends_on:
      app-postgres:
        condition: service_healthy
EOF

docker compose up -d --build