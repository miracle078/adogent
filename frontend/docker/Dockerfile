FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Add this debug step
RUN ls -la
RUN ls -la src/

RUN npm run build
