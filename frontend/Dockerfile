# Stage 1: Build the Vite bundle
FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve static bundle via Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose standard web port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
