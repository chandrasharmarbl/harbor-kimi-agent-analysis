FROM node:20-alpine
WORKDIR /app

# Scaffold the app inside the Docker build process
RUN npx -y @nestjs/cli new nestjs-app --package-manager npm --skip-install

WORKDIR /app/nestjs-app
# Add the postgres client dependency
RUN npm install pg

# Overwrite the generated files with our custom logic
COPY src/ src/

# Install all dependencies and build the app
RUN npm install
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start:prod"]
