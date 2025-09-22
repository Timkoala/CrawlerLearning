# 爬虫系统架构与执行流程文档

## 系统概述

本系统是一个基于Flask和Scrapy的Web爬虫管理平台，提供Web界面用于创建、管理和执行爬虫任务。

## 技术架构

- **前端**: HTML/CSS/JavaScript (Bootstrap)
- **后端**: Flask (Python Web框架)
- **爬虫引擎**: Scrapy (Python爬虫框架)
- **数据库**: SQLite (通过SQLAlchemy ORM)
- **进程管理**: Python multiprocessing模块

## 核心组件

### 1. Web界面 (Flask应用)
- 提供用户界面用于任务管理
- 通过RESTful API与后端通信
- 包含任务创建、执行控制、结果查看等功能

### 2. 爬虫引擎 (Scrapy)
- 实际执行网页爬取任务
- 支持深度爬取、反爬机制、代理设置等
- 可配置的中间件和管道

### 3. 数据库层 (SQLAlchemy)
- 持久化存储任务信息和爬取结果
- 提供数据模型和ORM操作

### 4. 进程管理
- 管理并发爬虫任务
- 控制任务的启动、停止和状态监控

## 执行流程详解

### 点击"开始爬取"按钮的完整执行流程

#### 1. 前端处理 (web/static/js/main.js)

```javascript
function startCrawl() {
    // 获取选中的任务ID
    const jobId = document.getElementById('selected-job').value;
    
    // 发送API请求到后端
    fetch(`/api/jobs/${jobId}/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'default-key'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新UI状态
            document.getElementById('start-crawl-btn').disabled = true;
            document.getElementById('stop-crawl-btn').disabled = false;
            simulateCrawlStatus(); // 模拟状态更新
        } else {
            alert('启动任务失败: ' + data.error);
        }
    })
    .catch(error => {
        alert('启动任务时发生错误');
    });
}
```

#### 2. 后端API处理 (web/__init__.py)

```python
@bp.route('/api/jobs/<int:job_id>/start', methods=['POST'])
@require_api_key
def api_start_job(job_id):
    # 从数据库获取任务
    job = CrawlJob.query.get_or_404(job_id)
    
    # 调用ProcessManager启动任务
    try:
        process_manager.start_job(job.id, job.target_url, job.max_depth)
        job.status = 'running'
        db.session.commit()
        return jsonify({'success': True, 'job': job.to_dict()})
    except Exception as e:
        job.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'error': str(e)}), 500
```

#### 3. 进程管理器处理 (crawler/process_manager.py)

```python
def start_job(self, job_id, target_url, max_depth=1):
    # 检查并发限制
    if len(self.engine.processes) >= self.max_concurrent_jobs:
        raise Exception("Maximum concurrent jobs reached")
        
    # 创建自定义爬虫类
    class CustomSpider(BaseSpider):
        name = f'spider_{job_id}'
        def __init__(self, *args, **kwargs):
            kwargs['start_urls'] = [target_url]
            kwargs['max_depth'] = max_depth
            super(CustomSpider, self).__init__(*args, **kwargs)
    
    # 调用CrawlerEngine启动爬虫
    return self.engine.start_crawl(job_id, CustomSpider, settings)
```

#### 4. 爬虫引擎处理 (crawler/engine.py)

```python
def start_crawl(self, job_id, spider_class, settings=None):
    # 创建进程间通信队列
    result_queue = Queue()
    
    # 在新进程中启动爬虫
    process = Process(target=self._run_spider, args=(job_id, spider_class, settings, result_queue))
    process.start()
    
    # 保存进程信息
    self.processes[job_id] = {
        'process': process,
        'start_time': time.time(),
        'result_queue': result_queue
    }
    
    return job_id

def _run_spider(self, job_id, spider_class, settings, result_queue):
    try:
        # 配置Scrapy设置
        scrapy_settings = get_project_settings()
        if settings:
            for key, value in settings.items():
                scrapy_settings.set(key, value)
        
        # 创建并启动爬虫进程
        process = CrawlerProcess(scrapy_settings)
        process.crawl(spider_class)
        process.start()  # 阻塞直到爬虫完成
        
        # 发送成功消息
        result_queue.put(('success', f'Job {job_id} completed successfully'))
    except Exception as e:
        # 发送错误消息
        result_queue.put(('error', str(e)))
```

## 数据模型

### 爬虫任务 (CrawlJob)
- `id`: 任务ID
- `name`: 任务名称
- `target_url`: 目标URL
- `max_depth`: 爬取深度
- `status`: 任务状态 (saved, running, completed, failed, stopped)
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 爬取结果 (CrawlResult)
- `id`: 结果ID
- `job_id`: 关联的任务ID
- `url`: 爬取的URL
- `title`: 页面标题
- `content`: 页面内容
- `scraped_at`: 爬取时间

## 配置文件

### Scrapy设置 (crawler/settings.py)
- 并发请求数设置
- 下载延迟设置
- 中间件配置
- 管道配置
- 代理设置
- 重试设置

### 中间件 (crawler/middlewares.py)
- 代理中间件
- 随机User-Agent中间件
- 反检测中间件

## 错误处理

系统包含多层错误处理机制：
1. **前端错误处理**: 捕获网络错误和API响应错误
2. **后端错误处理**: 捕获数据库操作错误和业务逻辑错误
3. **爬虫错误处理**: 捕获网络错误、解析错误等

## 安全机制

1. **API密钥验证**: 保护API端点
2. **输入验证**: 验证用户输入数据
3. **SQL注入防护**: 使用SQLAlchemy ORM

## 部署说明

1. 安装依赖: `pip install -r requirements.txt`
2. 初始化数据库: `python init_db.py`
3. 启动应用: `python run.py`

## 常见问题

1. **任务启动失败**: 检查Scrapy环境配置和权限设置
2. **数据库连接错误**: 检查数据库文件权限和路径
3. **API认证失败**: 检查API密钥配置

## 扩展建议

1. 添加任务调度功能
2. 实现分布式爬虫支持
3. 增加更丰富的数据可视化
4. 添加任务模板和批量创建功能