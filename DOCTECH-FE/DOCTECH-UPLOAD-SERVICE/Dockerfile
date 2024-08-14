# Stage 1: Build Stage
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of your app's source code from your host to your app container
COPY . .

# Build the project
RUN yarn build

# Stage 2: Serve Stage
FROM nginx:stable-alpine

# Set working directory to nginx asset directory
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy static assets from builder stage
COPY --from=builder /app/dist .

# Expose port 8001 on the container
EXPOSE 8001

# Complete Nginx configuration for SPA support and to listen on port 8001
RUN echo $'server {\n\
    listen 8001;\n\
    location / {\n\
        root   /usr/share/nginx/html;\n\
        index  index.html index.htm;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Nginx will start automatically when the container is run
