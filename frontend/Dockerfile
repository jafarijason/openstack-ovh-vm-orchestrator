# Frontend - React + Vite

# Build stage
FROM node:20 as builder

WORKDIR /app

# Copy package files
COPY package.json ./
COPY yarn.lock ./

RUN yarn install

# Copy source
COPY . .

# Set API URL for Docker environment
ENV VITE_API_URL=http://localhost:8000

# Build app
RUN npm run build

# Runtime stage
FROM node:20

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
