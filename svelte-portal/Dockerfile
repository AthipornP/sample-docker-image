# Use official Node image
FROM node:20-alpine
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install --silent

# Copy source code
COPY . .

# Build the app
RUN npm run build

EXPOSE 3000
ENV NODE_ENV=production

CMD ["npm", "start"]
