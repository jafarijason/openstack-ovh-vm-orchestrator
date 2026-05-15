# Frontend - React + Vite

# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build app
RUN npm run build

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run production build
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package.json /app/

# Expose port
EXPOSE 5174

# Start app
CMD ["serve", "-s", "dist", "-l", "5174"]
