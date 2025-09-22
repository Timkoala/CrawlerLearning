# Web爬虫管理系统

一个功能完整的Web爬虫管理系统，基于Flask和Scrapy构建，提供Web界面用于创建、管理和执行爬虫任务。

## 功能特性

1. **Web管理界面**
   - 任务创建和管理
   - 实时状态监控
   - 结果查看和导出

2. **爬虫引擎**
   - 基于Scrapy的强大爬虫能力
   - 支持深度爬取
   - 可配置的并发控制

3. **反爬机制**
   - 随机User-Agent
   - 代理支持
   - 请求延迟控制

4. **数据存储**
   - SQLite数据库存储
   - JSON格式导出

## 系统架构

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Web界面   │────│   Flask API  │────│  爬虫引擎    │
│ (HTML/CSS/  │    │ (Python)     │    │ (Scrapy)     │
│ JavaScript) │    │              │    │              │
└─────────────┘    └──────────────┘    └──────────────┘
                            │
                    ┌──────────────┐
                    │   数据库     │
                    │ (SQLite)     │
                    └──────────────┘
```

详细架构说明请参考:
- [系统架构文档](SYSTEM_ARCHITECTURE.md)
- [执行流程文档](START_CRAWL_FLOW.md)
- [故障排除指南](TROUBLESHOOTING.md)

## 安装部署

### 环境要求
- Python 3.7+
- pip包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd qwScrapy
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   ```bash
   python init_db.py
   ```

4. **启动应用**
   ```bash
   python run.py
   ```

5. **访问界面**
   在浏览器中打开 `http://localhost:5000`

## 使用指南

### 1. 创建爬虫任务

1. 访问"任务"页面
2. 在左侧表单中填写任务信息：
   - 任务名称：给任务起一个名字
   - 目标URL：要爬取的网站地址
   - 爬取深度：爬取的链接深度（1表示只爬取当前页面）
3. 点击"保存任务"按钮

### 2. 使用预定义任务

系统提供了菲律宾和新加坡的主要网站预定义任务：
- 菲律宾政府官网
- 菲律宾新闻网站
- Facebook等社交网站
- 新加坡政府官网
- 新加坡新闻网站

点击相应的按钮可以快速加载这些网站作为任务目标。

### 3. 执行爬虫任务

1. 在右侧"运行状态"面板中，从下拉菜单选择要执行的任务
2. 点击"开始爬取"按钮
3. 查看爬取状态面板中的实时信息

### 4. 查看爬取结果

1. 访问"结果"页面
2. 查看所有爬取到的数据
3. 可以按任务筛选结果

### 5. 系统设置

1. 访问"设置"页面
2. 配置爬虫参数：
   - User-Agent设置
   - 并发请求数
   - 下载延迟
   - 代理设置
   - 反检测设置

## API接口

系统提供RESTful API接口：

### 任务管理
- `GET /api/jobs` - 获取所有任务
- `POST /api/jobs` - 创建新任务
- `POST /api/jobs/<id>/start` - 启动任务
- `POST /api/jobs/<id>/stop` - 停止任务
- `DELETE /api/jobs/<id>` - 删除任务

### 系统设置
- `GET /api/settings` - 获取系统设置
- `POST /api/settings` - 更新系统设置

### 爬取结果
- `GET /api/results` - 获取爬取结果

所有API接口都需要在请求头中包含 `X-API-Key: default-key`

## 配置文件

### 数据库配置
- 数据库文件：`crawler.db` (SQLite)
- 数据库连接：在 `app.py` 中配置

### 爬虫配置
- Scrapy设置：`crawler/settings.py`
- 中间件：`crawler/middlewares.py`
- 管道：`crawler/pipelines.py`

## 安全说明

1. **API密钥保护**：所有API端点都需要API密钥验证
2. **输入验证**：对用户输入进行严格验证
3. **错误处理**：避免敏感信息泄露

## 故障排除

遇到问题时请参考 [故障排除指南](TROUBLESHOOTING.md)

常见问题：
1. 任务无法启动：检查Scrapy环境和权限设置
2. 数据库连接失败：检查数据库文件权限
3. API认证失败：检查API密钥配置

## 扩展开发

### 添加新的爬虫功能
1. 在`crawler/spiders/`目录下创建新的爬虫类
2. 在`crawler/pipelines.py`中添加数据处理管道
3. 在`crawler/middlewares.py`中添加中间件

### 自定义UI
1. 修改`web/templates/`中的HTML模板
2. 更新`web/static/css/`中的样式文件
3. 调整`web/static/js/`中的JavaScript逻辑

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站的robots.txt规则。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。