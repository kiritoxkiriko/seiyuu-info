# nsy 情报站

面向日本女声优信息聚合的站点。后端使用 FastAPI 抓取、缓存和提供 API，前端使用 Astro + React + TypeScript + Tailwind CSS 渲染页面。当前默认部署方式是 Docker Compose：一个后端容器、一个前端容器，定时同步运行在后端进程内。

## 功能

- 可配置声优列表，当前包含羊宮妃那、青木陽菜
- 展示个人资料、公式照和代表角色
- 展示 Eventernote 活动时间线，支持筛选、搜索、分页和即将开始/已结束状态
- 展示 X 动态，过滤 repost/reply，支持全部、带图片、仅文字筛选
- 推文默认折叠长文和图片，展开后查看全文、大图和高清下载
- event 和 SNS 支持独立抓取/展示时间窗、SQLite 落库缓存、原文/中文切换
- 后端进程内定时同步，默认每 10 分钟同步 SNS、每 1 小时同步 event
- 图片存储保留 provider 抽象，当前实现本地 `/media`

## 项目结构

```text
.
├── app/                    # FastAPI 应用
│   ├── api/v1/endpoints/   # API 路由
│   ├── core/               # 配置
│   ├── schemas/            # Pydantic 模型
│   ├── services/           # 数据库、抓取、翻译、存储、调度
│   └── main.py             # FastAPI app factory
├── data/actors.json        # 声优配置
├── migrations/             # SQLite schema
├── scripts/sync_data.py    # 手动同步脚本
├── tests/                  # 后端测试
├── web/                    # Astro 前端
├── Dockerfile              # 后端镜像
├── web/Dockerfile          # 前端镜像
└── docker-compose.yaml     # 本地/服务器部署编排
```

## 快速部署

准备环境变量。可以从 `.env.example` 复制一份：

```bash
cp .env.example .env
```

真实 X 数据需要配置：

```bash
X_BEARER_TOKEN=...
```

如需中文翻译，再配置：

```bash
TRANSLATION_PROVIDER=deepl
DEEPL_API_KEY=...
```

拉取镜像并启动：

```bash
docker compose pull
docker compose up -d
```

访问：

- 前端：`http://localhost:4321`
- 后端：`http://localhost:8787`

查看日志：

```bash
docker compose logs -f api
docker compose logs -f web
```

Compose 默认把后端数据目录绑定到宿主机 `./data`，SQLite 数据库位于 `./data/nsy.sqlite3`，图片位于 `./data/media`。
默认镜像来自 GHCR：

- `ghcr.io/kiritoxkiriko/seiyuu-info-api:${IMAGE_TAG:-latest}`
- `ghcr.io/kiritoxkiriko/seiyuu-info-web:${IMAGE_TAG:-latest}`

如需固定版本，可以在 `.env` 中设置：

```bash
IMAGE_TAG=v0.1.1
```

立即同步一次数据：

```bash
docker compose exec api python scripts/sync_data.py
```

只同步 SNS：

```bash
docker compose exec api python scripts/sync_data.py --no-events
```

只同步 event：

```bash
docker compose exec api python scripts/sync_data.py --no-sns
```

## 本地开发

后端：

```bash
uv sync
set -a
source .env
set +a
uv run uvicorn app.main:app --host localhost --port 8787
```

前端：

```bash
cd web
npm install
PUBLIC_API_BASE_URL=http://localhost:8787 npm run dev
```

手动同步数据：

```bash
set -a
source .env
set +a
uv run python scripts/sync_data.py
```

运行测试：

```bash
uv run pytest
cd web
ASTRO_ADAPTER=node ASTRO_TELEMETRY_DISABLED=1 npm run build
```

## 配置

核心配置都可以通过环境变量覆盖：

- `ALLOWED_ORIGINS=http://localhost:4321`：后端 CORS origin
- `DATA_CACHE_ENABLED=true`：开启 API 缓存读写
- `DATABASE_URL=sqlite:///data/nsy.sqlite3`：SQLite 数据库路径
- `EVENT_FETCH_PAST_DAYS=183` / `EVENT_FETCH_FUTURE_DAYS=183`：event 抓取窗口
- `SNS_FETCH_PAST_DAYS=183`：推文抓取窗口
- `EVENT_DISPLAY_PAST_DAYS=183` / `EVENT_DISPLAY_FUTURE_DAYS=183`：event 展示窗口
- `SNS_DISPLAY_PAST_DAYS=183`：SNS 展示窗口
- `SCHEDULER_ENABLED=true`：是否启用后端进程内定时同步
- `SNS_SYNC_INTERVAL_MINUTES=10`：SNS 同步间隔
- `EVENT_SYNC_INTERVAL_MINUTES=60`：event 同步间隔
- `MEDIA_ROOT=data/media` / `MEDIA_PUBLIC_PREFIX=/media`：本地图片存储路径和访问前缀
- `X_BEARER_TOKEN=...`：X API v2 Bearer Token
- `TRANSLATION_PROVIDER=none|deepl`：翻译 provider
- `DEEPL_API_KEY=...`：DeepL API Key

Docker Compose 默认会开启 `SCHEDULER_ENABLED=true`。本地 `uvicorn` 开发时可以按需关闭，避免频繁抓取真实数据。

## 数据源

声优基础信息配置在 `data/actors.json`：

- `actors`：个人资料、公式照、SNS 链接、Eventernote 搜索 URL
- `events`：本地 fallback event 数据
- `sns`：本地 fallback SNS 数据

后端 API 在 `cache=true` 时优先读取 SQLite；库里没有数据或手动同步时，会从 Eventernote 和 X 拉取真实数据并 upsert，避免重复抓取。

语言通过 `language` 参数切换：

```bash
curl "http://localhost:8787/api/v1/actors/aoki-hina?event_source=eventernote&sns_source=x&language=zh&cache=true"
```

默认 `TRANSLATION_PROVIDER=none` 会把原文写入中文字段，方便无 Key 开发；配置 DeepL 后重新同步即可写入真实中文翻译。

## 镜像发布

仓库包含 GitHub Actions workflow：

- `.github/workflows/release-images.yml`

创建 GitHub Release 后会构建并推送：

- `ghcr.io/kiritoxkiriko/seiyuu-info-api`
- `ghcr.io/kiritoxkiriko/seiyuu-info-web`

镜像标签包含：

- `latest`
- Git tag
- commit SHA
