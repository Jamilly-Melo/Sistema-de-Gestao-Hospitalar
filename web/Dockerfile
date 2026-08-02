FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# NEXT_PUBLIC_* é inlinado por `npm run build` em tempo de BUILD, não lido em
# runtime — por isso precisa entrar como build ARG/ENV aqui (ver
# docker-compose.yaml, build.args do serviço `web`), e não como `environment:`
# do compose, que só afetaria o processo em runtime.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
