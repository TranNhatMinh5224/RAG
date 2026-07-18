FROM node:20-alpine

WORKDIR /app

# Copy package.json and install dependencies
# We will create package.json using Vite later, so this will only run if package.json exists.
# We mount code as volume and run dev server.

COPY package*.json ./
RUN if [ -f package.json ]; then npm install; fi

EXPOSE 5173

# Chạy server Vite, expose ra host
CMD ["npm", "run", "dev", "--", "--host"]
