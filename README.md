# nsy 情报站

面向日本女声优信息聚合的 Cloudflare Workers 项目。当前采用后端优先结构：仓库根目录是 Python Workers + FastAPI API，前端 Astro + React + TypeScript + Tailwind CSS 应用放在 `web/`。

## 功能

- 可配置声优列表，当前包含羊宮妃那、青木陽菜
- 展示个人信息、公式/艺人照和代表角色
- 展示 event 时间线，支持类别筛选、关键词搜索和分页
- 展示 X/SNS 动态，后端默认过滤 X repost/reply 和 Instagram 展示，仅返回 original/quote
- SNS 列表支持分页；单条动态默认折叠长文和图片，展开后查看全文与大图
- Eventernote event 和 X posts 支持独立的抓取/显示时间窗、落库缓存和原文/中文切换
- Cloudflare Cron 定时抓取：默认每 10 分钟同步 SNS、每 1 小时同步 event
- 图片存储保留 provider 边界，当前实现本地 `/media` 静态文件

## 项目结构

```text
.
├── app/                    # 标准 FastAPI 应用包
│   ├── api/v1/endpoints/   # API v1 路由实现
│   ├── core/               # 配置与核心工具
│   ├── schemas/            # Pydantic 请求/响应模型
│   ├── services/           # 数据仓库、缓存、Eventernote、SNS provider
│   └── main.py             # FastAPI app factory
├── data/actors.json        # 声优、活动、SNS 配置数据
├── migrations/             # SQLite/D1 兼容 schema
├── scripts/sync_data.py    # 抓取并落库脚本
├── tests/                  # 后端 API 测试
├── worker.py               # Cloudflare Python Workers ASGI 入口
├── pyproject.toml          # 后端依赖与 pytest 配置
├── wrangler.jsonc          # 后端 Worker 配置
└── web/                    # Astro 前端 Worker 项目
    ├── src/                # 前端源码
    ├── wrangler.jsonc      # 前端 Worker 配置
    └── package.json        # 前端脚本
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

前端默认通过 `PUBLIC_API_BASE_URL=http://localhost:8787` 访问后端，API 路径为 `/api/v1/*`。后端没启动时，前端会使用内置 fallback 数据，方便先看页面。

初始化/刷新本地缓存库：

```bash
set -a
source .env
set +a
.venv/bin/python scripts/sync_data.py
```

如果要在本地验证 Cloudflare 的 `scheduled()` 行为，需要用 Worker runtime 而不是 `uvicorn`。官方 Python Workers 会暴露一个测试路由：

```bash
uv run pywrangler dev --test-scheduled
curl "http://localhost:8787/cdn-cgi/handler/scheduled?cron=*+*+*+*+*"
```

## 配置声优

编辑 `data/actors.json`：

- `actors`：基础资料、公式照、照片墙、SNS 链接、Eventernote 搜索 URL
- `events`：时间线数据，`category` 可选 `live`、`stage`、`talk`、`release`、`broadcast`、`other`
- `sns`：动态数据，`kind` 为 `repost` 或 `reply` 时不会展示

## 真实数据源

Event 默认按时间倒序返回，并限制在配置的显示窗口内。可通过 Eventernote 公开页面拉取真实 event：

```bash
curl "http://localhost:8787/api/v1/events?actor_id=yomiya-hina&source=eventernote&cache=true"
```

前端详情请求默认会带 `event_source=eventernote&sns_source=x&cache=true`。开启缓存时后端优先读库；库里没有数据时才抓取并 upsert，避免重复抓取。

SNS 默认按 `postedAt` 倒序返回，并限制在配置的显示窗口内。X 使用 API v2 user posts timeline，通过 `exclude=retweets,replies` 过滤转发和回复；Instagram 不再进入 SNS 展示。

语言通过 `language` 参数切换：

```bash
curl "http://localhost:8787/api/v1/actors/aoki-hina?event_source=eventernote&sns_source=x&language=zh&cache=true"
```

中文字段在抓取/同步时写入库。默认 `TRANSLATION_PROVIDER=none` 会把原文写入中文字段，方便本地无 Key 开发；如需真实翻译，配置 `TRANSLATION_PROVIDER=deepl` 和 `DEEPL_API_KEY` 后重新运行同步脚本。

环境变量示例见 `.env.example`。

显式调试 X 数据：

```bash
set -a
source .env
set +a
uv run uvicorn app.main:app --host localhost --port 8787
curl "http://localhost:8787/api/v1/sns?actor_id=aoki-hina&source=x&cache=true"
```

## 数据库与图片存储

本地缓存使用 SQLite，默认路径 `data/nsy.sqlite3`，已被 `.gitignore` 忽略。schema 位于 `migrations/0001_cache.sql`，与 Cloudflare D1 兼容。

相关开关：

- `DATA_CACHE_ENABLED=true`：开启 API 读写缓存
- `DATABASE_URL=sqlite:///data/nsy.sqlite3`：本地 SQLite
- `D1_BINDING=DB`：Cloudflare Worker 上的 D1 binding 名称
- `EVENT_FETCH_PAST_DAYS=183` / `EVENT_FETCH_FUTURE_DAYS=183`：event 抓取与落库窗口
- `SNS_FETCH_PAST_DAYS=183`：推文抓取与落库窗口
- `EVENT_DISPLAY_PAST_DAYS=183` / `EVENT_DISPLAY_FUTURE_DAYS=183`：event 接口展示窗口
- `SNS_DISPLAY_PAST_DAYS=183`：推文接口展示窗口
- `MEDIA_ROOT=data/media` / `MEDIA_PUBLIC_PREFIX=/media`：本地图片存储目录与访问前缀

API 支持 `cache=true|false` 请求级覆盖，便于调试 live fetch 和缓存读取。

## 定时抓取

部署到 Cloudflare Workers 后，根 Worker 配置了每分钟一次的 Cron Trigger。真正的业务频率不写死在 cron 表达式里，而是由数据库里的 `job_runs` 和下面三个配置共同控制：

- `SCHEDULER_ENABLED=true|false`：是否启用定时抓取
- `SNS_SYNC_INTERVAL_MINUTES=10`：SNS 抓取间隔，默认 10 分钟
- `EVENT_SYNC_INTERVAL_MINUTES=60`：event 抓取间隔，默认 1 小时

这样做的原因是 Cloudflare Cron 的最小粒度是 1 分钟，而业务间隔需要可配置。Worker 每分钟被唤起一次，再根据上次执行时间决定这次是否真正抓取。

定时抓取使用和缓存相同的持久化 schema，新增 `job_runs` 表记录每类任务的上次执行时间。上线时建议配合 D1 使用；否则 Worker 侧的本地文件存储不具备可靠持久性。

## Cloudflare 部署

后端 Python Worker：

```bash
uv run pywrangler deploy
```

本地开发默认用 `uv run uvicorn`，这样更符合标准 FastAPI 项目习惯。`pywrangler` 只在需要模拟或部署 Cloudflare Python Workers runtime 时使用。

如需在 Worker 上启用落库缓存，创建 D1 并绑定为 `DB`：

```bash
npx wrangler d1 create nsy-station
npx wrangler d1 execute nsy-station --file migrations/0001_cache.sql
```

然后把返回的 D1 信息加入 `wrangler.jsonc`：

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "nsy-station",
      "database_id": "<database-id>"
    }
  ],
  "vars": {
    "DATA_CACHE_ENABLED": "true",
    "D1_BINDING": "DB",
    "SCHEDULER_ENABLED": "true",
    "SNS_SYNC_INTERVAL_MINUTES": "10",
    "EVENT_SYNC_INTERVAL_MINUTES": "60"
  }
}
```

生产环境的 `X_BEARER_TOKEN`、`DEEPL_API_KEY` 不要写进 `wrangler.jsonc`，用 Wrangler secret 或 Cloudflare Dashboard 配置：

```bash
npx wrangler secret put X_BEARER_TOKEN
npx wrangler secret put DEEPL_API_KEY
```

前端 Worker：

```bash
cd web
npm run build
npx wrangler deploy
```

部署后把 `web/wrangler.jsonc` 里的 `PUBLIC_API_BASE_URL` 改成后端 Worker URL，例如：

```jsonc
{
  "vars": {
    "PUBLIC_API_BASE_URL": "https://nsy-station-api.<account>.workers.dev"
  }
}
```

再重新部署前端。

## 验证

```bash
uv run pytest
```

```bash
cd web
npm run build
```

## 资料来源

- 羊宮妃那：青二プロダクション公式プロフィール
- 青木陽菜：響公式プロフィール、BM-ECHOES artist profile
- Cloudflare Workers 官方文档：Astro on Workers、Python Workers、FastAPI on Python Workers
