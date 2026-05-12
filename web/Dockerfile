FROM node:22-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

FROM deps AS build

WORKDIR /app

COPY . .

ENV ASTRO_TELEMETRY_DISABLED=1 \
    ASTRO_ADAPTER=node

RUN npm run build

FROM node:22-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=4321 \
    INTERNAL_API_BASE_URL=http://api:8787

COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./package.json

EXPOSE 4321

CMD ["node", "./dist/server/entry.mjs"]
