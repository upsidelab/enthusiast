FROM node:20

ARG VITE_API_BASE
ARG VITE_WS_BASE
ARG PORT

ENV VITE_API_BASE=$VITE_API_BASE
ENV VITE_WS_BASE=$VITE_WS_BASE
ENV PORT=$PORT

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm

RUN pnpm install

COPY . .

RUN chmod u+x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
