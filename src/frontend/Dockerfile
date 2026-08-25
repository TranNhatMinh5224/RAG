# =========================================
# STAGE 1: Development (Vite Dev Server)
# =========================================
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# =========================================
# STAGE 2: Build (Biên dịch React + Vite thành file tĩnh)
# =========================================
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# =========================================
# STAGE 3: Production (Nginx Web Server - Bỏ hoàn toàn Node.js/Vite ở runtime)
# =========================================
FROM nginx:alpine AS production
# Copy file tĩnh vừa được biên dịch vào thư mục chứa web của Nginx
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
