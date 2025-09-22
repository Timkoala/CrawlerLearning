# Web 爬虫管理系统（Flask + Scrapy）

一个基于 Flask + Scrapy 的可视化网页爬虫平台：支持任务管理、分批(run)执行、结果筛选/分页/导出/删除、基础反检测、REST API 与前端页面联动。

- Python: Flask + SQLAlchemy + SQLite
- 爬虫: Scrapy（多进程运行，子进程内自动注入 Flask 应用上下文）
- 前端: Bootstrap + 原生 JavaScript

## 目录结构

```
E:\Github\CrawlerLearning
├─ app.py                     # Flask 应用工厂，自动建表+轻量迁移
├─ run.py                     # 开发启动入口
├─ web/                       # Web 蓝图、模板与静态资源
│  ├─ __init__.py             # 路由与 API（jobs/results/runs/settings/sites）
│  ├─ templates/              # 页面模板（首页/任务/结果/设置）
│  └─ static/js/main.js       # 前端逻辑：任务、运行状态、结果分页/筛选/批量操作
├─ crawler/                   # Scrapy 工程
│  ├─ engine.py               # 多进程调度，引擎与 run 生命周期
│  ├─ spiders/custom_spider.py# 可携带自定义选择器的通用爬虫（兼容 Scrapy 2.13 的 start()）
│  ├─ pipelines.py            # JSON/数据库写入（含 run_id）
│  ├─ middlewares.py          # 随机 UA、延迟等中间件
│  └─ settings.py             # Scrapy 配置：重试/允许403/中间件/管道等
├─ models/
│  ├─ job.py                  # 模型：CrawlJob、CrawlRun、CrawlResult
│  └─ database.py             # 常用表操作封装
├─ config/
│  ├─ sites.txt               # 预置站点（支持第5列 JSON 选择器）
│  └─ sites_config.py         # 预置站点解析（含 selectors 字段）
└─ instance/crawler.db        # SQLite 数据库（开发时自动创建）
```

## 快速开始

1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 启动服务（开发）
```bash
python run.py
```
浏览器打开 `http://localhost:5000`

3) API 访问需请求头携带：
```
X-API-Key: default-key
```
（可通过环境变量 `API_KEY` 覆盖）

## 功能一览

- 任务管理
  - 新建/编辑（PUT）/删除
  - 预置站点一键填充（支持选择器）
- 爬取执行
  - 多进程调度；每次执行生成独立批次（run）
  - 实时轮询状态（运行中/完成/失败/停止）
- 结果管理
  - 分任务、分批次筛选；关键词搜索；分页
  - 单条：预览/复制/下载/删除
  - 批量：勾选删除；按当前批次一键删除
  - 批次：预览全部/下载全部（JSON）
- 反检测基础能力
  - 随机 UA、允许 403/404 与重试、下载延时；可扩展代理

## 数据模型

- `CrawlJob`：任务
  - `name`, `target_url`, `max_depth`, `custom_rules(JSON)`, `status`
- `CrawlRun`：执行批次
  - `job_id`, `status`, `max_depth`, `started_at`, `ended_at`, `stats_json`
- `CrawlResult`：爬取结果
  - `job_id`, `run_id`, `url`, `title`, `content`, `scraped_data(JSON)`, `scraped_at`

应用启动会自动建表，并执行轻量迁移（为旧库增加 `crawl_result.run_id` 列）。

## 选择器填写指南（非常重要）

- 标题选择器（示例）
  - `h1.title::text`
  - `meta[property='og:title']::attr(content)`
- 内容选择器（示例）
  - `.article-content p::text`
  - `div.story-content p::text`
- 自定义字段（逐行填写 `字段名=CSS选择器`）
  - `author=.author-name::text`
  - `date=.publish-date::text`
  - `source=meta[name='og:site_name']::attr(content)`

说明：
- `::text` 获取文本；`::attr(href)` 获取链接；空格分层级，如 `.content p::text`
- 内容会自动拼接并截断（默认 500~1000 字）

## 预置站点（config/sites.txt）

- 支持格式（5 列）：
```
类别|国家|网站名称(中文)|URL|选择器配置(JSON)
```
- 选择器配置示例：
```json
{"title_selector":"h1.story-title::text","content_selector":"div.story-content p::text","custom_fields":{"date":"div.timestamp::text","author":"span.byline::text"}}
```
- 未提供第5列时，使用默认规则（`<title>` 与 `body ::text`）

前端会按「国家 | 类别」分组展示，点击预置项即可回填任务表单。

## 前后端工作流

1) 新建任务（或编辑任务）
   - 前端 `POST /api/jobs`（或 `PUT /api/jobs/<id>`）保存
2) 启动执行
   - `POST /api/jobs/<id>/start` → 引擎创建 `CrawlRun` 并在子进程内运行 Scrapy
3) 采集入库
   - `pipelines.DatabasePipeline` 将每条 item 写入 `CrawlResult(job_id, run_id, ...)`
4) 查看结果
   - 结果页通过 `/api/results` 分页加载；可按 `job_id/run_id/q` 筛选
5) 批量/批次操作
   - 勾选删除 → `/api/results/batch_delete`（ids）
   - 按批次删除 → `/api/results/batch_delete`（run_id，连同 `CrawlRun` 一并删除）
   - 批次预览/下载 → `/api/results/export?run_id=&format=json|csv`

## API 文档（需 Header: X-API-Key）

- 任务 Jobs
  - `GET /api/jobs` 列表
  - `POST /api/jobs` 创建（body: `name, target_url, max_depth, custom_rules`）
  - `GET /api/jobs/<id>` 详情（含实时状态合并）
  - `PUT /api/jobs/<id>` 更新
  - `DELETE /api/jobs/<id>` 删除（会尝试先停止）
  - `POST /api/jobs/<id>/start` 启动
  - `POST /api/jobs/<id>/stop` 停止

- 批次 Runs
  - `GET /api/runs?job_id=` 按任务列出批次（倒序）

- 结果 Results（分页）
  - `GET /api/results?page=&page_size=&job_id=&run_id=&q=`
    - 返回：`{ total, page, page_size, items: [CrawlResult...] }`
  - `DELETE /api/results/<id>` 删除单条
  - `POST /api/results/batch_delete` 批量删除
    - body: `{ ids: [1,2] }` 或 `{ run_id: 123 }`（同时删除该 `CrawlRun`）
  - `GET /api/results/export?format=json|csv&job_id=&run_id=&q=` 导出

- 预置站点 Sites
  - `GET /api/sites` 返回 `[{ category,country,name,url,selectors? }]`

- 设置 Settings
  - `GET /api/settings` / `POST /api/settings`

## 运行与配置

- 环境变量
  - `PORT`（默认 5000）：Flask 端口
  - `API_KEY`（默认 `default-key`）：接口鉴权 Key
- 数据库
  - 默认 `sqlite:///crawler.db`（项目根目录）
- Scrapy 关键设置（`crawler/settings.py`）
  - `HTTPERROR_ALLOWED_CODES = [403, 404]`
  - `RETRY_ENABLED = True`, `RETRY_TIMES = 2`
  - `DOWNLOADER_MIDDLEWARES`: `RandomUserAgentMiddleware`
  - `DOWNLOAD_DELAY = 0.5`（可按需调整）
  - `ITEM_PIPELINES`: JSON 与数据库存储

## 反检测建议

- 已内置：随机 UA、允许 403/404 与重试、延时
- 建议扩展：
  - 代理池（在 `middlewares.py` 启用 `ProxyMiddleware` 并在 settings 配置 `PROXY_LIST`）
  - 指定 Referer/Cookie/Header（可在 Spider 中按站点加定制化逻辑）
  - 降低并发与拉长延迟；开启 AutoThrottle（需要在 settings 显式开启）

## 常见问题（FAQ）

- 403 或无结果
  - 很多政府/新闻站点需要代理或严苛 Header；先尝试更换 UA/增加延时/配置代理
- 结果页“加载失败”
  - 确保数据库已迁移（应用启动已自动迁移）；若日志出现 `no such column run_id`，重启后应修复
- 编辑任务导致重复创建
  - 前端已使用 `PUT` 更新；确保按钮文案显示“更新任务”时再提交
- 按批次删除后下拉未刷新
  - 已在前端调用后 `loadRuns(); loadResults();` 强制刷新，如仍异常请清浏览器缓存并重试

## 开发与调试

- 日志
  - Flask 与 Scrapy 均设为 INFO 级别，可在 `app.py`/`crawler/settings.py` 调整
- 子进程与上下文
  - 引擎在子进程内推入 Flask 应用上下文，保证 SQLAlchemy 在 Pipeline 可用
- 代码风格
  - 遵循清晰命名与早返回；新增模块请保持一致风格

## 许可证与声明

本项目仅用于学习与研究。使用本系统进行采集时，请遵守目标站点的服务条款与所在地区法律法规。

## 贡献

欢迎提交 Issue / PR 改进功能、补充预置站点（含第5列 JSON 选择器）。