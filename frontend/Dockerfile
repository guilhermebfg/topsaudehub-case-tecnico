FROM node:20-bookworm-slim

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm ci --no-audit --no-fund

COPY . .

ENV NG_CLI_ANALYTICS=ci
EXPOSE 4200

CMD ["npm","run","start","--","--host","0.0.0.0","--port","4200"]
