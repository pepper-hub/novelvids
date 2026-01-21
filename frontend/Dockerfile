# Frontend Dockerfile
FROM node:22-alpine as base

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

FROM base as development

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]

FROM base as build

COPY . .

RUN npm run build

FROM nginx:alpine as production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
