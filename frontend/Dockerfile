FROM node:20 as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Development stage
FROM node:20 as development

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies including dev dependencies
RUN npm install

# Set environment variables
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Start the development server
CMD ["npm", "run", "dev"]

# Production stage
FROM node:20 as production

WORKDIR /app

# Copy only necessary files from build stage
COPY --from=build /app/.output /app/.output
COPY --from=build /app/package.json /app/package.json

# Set environment variables
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Start the application
CMD ["node", ".output/server/index.mjs"]
