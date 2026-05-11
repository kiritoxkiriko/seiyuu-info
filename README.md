# nsy 情报站

面向日本女声优信息聚合的 Cloudflare Workers 项目。当前采用后端优先结构：仓库根目录是 Python Workers + FastAPI API，前端 Astro + React + TypeScript + Tailwind CSS 应用放在 `web/`。

## 功能

- 可配置声优列表，当前包含羊宮妃那、青木陽菜
- 展示个人信息、公式/艺人照、照片墙和代表角色
- 展示 event 时间线，支持类别筛选和关键词搜索
- 展示 SNS 动态，后端默认过滤 X repost/reply，仅返回 original/quote
- Eventernote 和 SNS 都保留 provider 边界，后续可替换成真实抓取或官方 API

## 项目结构

```text
.
├── app/                    # 标准 FastAPI 应用包
│   ├── api/v1/endpoints/   # API v1 路由实现
│   ├── core/               # 配置与核心工具
│   ├── schemas/            # Pydantic 请求/响应模型
│   ├── services/           # 数据仓库、Eventernote、SNS provider
│   └── main.py             # FastAPI app factory
├── data/actors.json        # 声优、活动、SNS 配置数据
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
uv run uvicorn app.main:app --host localhost --port 8787
```

前端：

```bash
cd web
npm install
PUBLIC_API_BASE_URL=http://localhost:8787 npm run dev
```

前端默认通过 `PUBLIC_API_BASE_URL=http://localhost:8787` 访问后端，API 路径为 `/api/v1/*`。后端没启动时，前端会使用内置 fallback 数据，方便先看页面。

## 配置声优

编辑 `data/actors.json`：

- `actors`：基础资料、公式照、照片墙、SNS 链接、Eventernote 搜索 URL
- `events`：时间线数据，`category` 可选 `live`、`stage`、`talk`、`release`、`broadcast`、`other`
- `sns`：动态数据，`kind` 为 `repost` 或 `reply` 时不会展示

## Cloudflare 部署

后端 Python Worker：

```bash
uv run pywrangler deploy
```

本地开发默认用 `uv run uvicorn`，这样更符合标准 FastAPI 项目习惯。`pywrangler` 只在需要模拟或部署 Cloudflare Python Workers runtime 时使用。

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
