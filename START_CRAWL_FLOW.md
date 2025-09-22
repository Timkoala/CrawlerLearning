# "开始爬取"按钮执行流程详细说明

## 概述

本文档详细描述了用户在Web界面点击"开始爬取"按钮后，系统各组件之间的交互流程和执行逻辑。

## 执行流程

### 1. 前端触发 (JavaScript)

当用户点击"开始爬取"按钮时，触发以下JavaScript函数：

```javascript
function startCrawl() {
    // 步骤1: 获取选中的任务ID
    const jobId = document.getElementById('selected-job').value;
    if (!jobId) {
        alert('请选择一个任务');
        return;
    }
    
    // 步骤2: 发送API请求到后端
    fetch(`/api/jobs/${jobId}/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'default-key'
        }
    })
    .then(response => {
        // 步骤3: 处理HTTP响应
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        // 步骤4: 处理API返回数据
        if (data.success) {
            console.log('Starting crawl for job:', jobId);
            
            // 步骤5: 更新UI状态
            document.getElementById('start-crawl-btn').disabled = true;
            document.getElementById('stop-crawl-btn').disabled = false;
            
            // 步骤6: 启动状态更新模拟
            simulateCrawlStatus();
        } else {
            alert('启动任务失败: ' + data.error);
        }
    })
    .catch(error => {
        // 步骤7: 处理网络或解析错误
        console.error('Error starting job:', error);
        alert('启动任务时发生错误: ' + error.message);
    });
}
```

### 2. 后端API处理 (Flask路由)

Flask接收到请求后，调用相应的路由处理函数：

```python
@bp.route('/api/jobs/<int:job_id>/start', methods=['POST'])
@require_api_key
def api_start_job(job_id):
    """
    启动指定ID的爬虫任务
    """
    # 步骤1: 从数据库获取任务
    job = CrawlJob.query.get_or_404(job_id)
    
    # 步骤2: 调用进程管理器启动任务
    try:
        # 步骤2.1: 调用ProcessManager启动任务
        process_manager.start_job(job.id, job.target_url, job.max_depth)
        
        # 步骤2.2: 更新任务状态为"运行中"
        job.status = 'running'
        from app import db
        db.session.commit()
        
        # 步骤2.3: 返回成功响应
        return jsonify({'success': True, 'job': job.to_dict()})
    except Exception as e:
        # 步骤3: 处理启动失败情况
        job.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'error': str(e)}), 500
```

### 3. 进程管理器处理 (ProcessManager)

ProcessManager负责管理爬虫任务的进程：

```python
class ProcessManager:
    def __init__(self):
        self.engine = CrawlerEngine()
        self.max_concurrent_jobs = 5  # 最大并发任务数限制
        
    def start_job(self, job_id, target_url, max_depth=1):
        """
        启动一个爬虫任务
        """
        # 步骤1: 检查并发限制
        if len(self.engine.processes) >= self.max_concurrent_jobs:
            raise Exception("Maximum concurrent jobs reached")
            
        # 步骤2: 创建爬虫设置
        settings = {
            'MAX_DEPTH': max_depth
        }
        
        # 步骤3: 为该任务创建自定义爬虫类
        class CustomSpider(BaseSpider):
            name = f'spider_{job_id}'
            
            def __init__(self, *args, **kwargs):
                kwargs['start_urls'] = [target_url]
                kwargs['max_depth'] = max_depth
                super(CustomSpider, self).__init__(*args, **kwargs)
        
        # 步骤4: 调用爬虫引擎启动任务
        return self.engine.start_crawl(job_id, CustomSpider, settings)
```

### 4. 爬虫引擎处理 (CrawlerEngine)

CrawlerEngine负责实际的爬虫进程管理：

```python
class CrawlerEngine:
    def __init__(self):
        self.processes = {}  # 存储运行中的进程
        self.results = {}    # 存储结果
        
    def start_crawl(self, job_id, spider_class, settings=None):
        """
        在新进程中启动爬虫任务
        """
        # 步骤1: 检查任务是否已在运行
        if job_id in self.processes:
            raise ValueError(f"Job {job_id} is already running")
            
        # 步骤2: 创建进程间通信队列
        result_queue = Queue()
        
        # 步骤3: 在新进程中启动爬虫
        process = Process(target=self._run_spider, 
                         args=(job_id, spider_class, settings, result_queue))
        process.start()
        
        # 步骤4: 存储进程信息
        self.processes[job_id] = {
            'process': process,
            'start_time': time.time(),
            'result_queue': result_queue
        }
        
        return job_id
    
    def _run_spider(self, job_id, spider_class, settings, result_queue):
        """
        在独立进程中运行爬虫
        """
        try:
            # 步骤1: 配置Scrapy设置
            scrapy_settings = get_project_settings()
            if settings:
                for key, value in settings.items():
                    scrapy_settings.set(key, value)
            
            # 步骤2: 创建并启动爬虫进程
            process = CrawlerProcess(scrapy_settings)
            process.crawl(spider_class)
            process.start()  # 这里会阻塞直到爬虫完成
            
            # 步骤3: 发送成功消息
            result_queue.put(('success', f'Job {job_id} completed successfully'))
        except Exception as e:
            # 步骤4: 发送错误消息
            result_queue.put(('error', str(e)))
```

### 5. 实际爬虫执行 (Scrapy Spider)

BaseSpider是所有爬虫任务的基础类：

```python
class BaseSpider(scrapy.Spider):
    name = 'base_spider'
    
    def __init__(self, start_urls=None, max_depth=1, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls or []
        self.max_depth = int(max_depth)
        
    def start_requests(self):
        """
        开始请求处理
        """
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={'depth': 1})
            
    def parse(self, response):
        """
        解析响应内容
        """
        # 步骤1: 提取页面数据
        item = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': ' '.join(response.css('body ::text').getall()).strip(),
            'links': response.css('a::attr(href)').getall()
        }
        
        yield item
        
        # 步骤2: 根据深度设置决定是否继续爬取
        current_depth = response.meta.get('depth', 1)
        if current_depth < self.max_depth:
            for link in response.css('a::attr(href)').getall():
                # 转换相对URL为绝对URL
                absolute_url = response.urljoin(link)
                yield Request(absolute_url, callback=self.parse, 
                             meta={'depth': current_depth + 1})
```

## 数据流向

1. **用户操作**: 点击"开始爬取"按钮
2. **前端请求**: JavaScript发送POST请求到`/api/jobs/{job_id}/start`
3. **后端处理**: Flask路由处理请求，调用ProcessManager
4. **进程管理**: ProcessManager创建自定义爬虫类，调用CrawlerEngine
5. **引擎启动**: CrawlerEngine在新进程中启动Scrapy爬虫
6. **爬虫执行**: Scrapy爬虫开始执行网页爬取任务
7. **结果返回**: 执行结果通过队列返回给前端
8. **UI更新**: 前端根据结果更新界面状态

## 错误处理流程

### 前端错误处理
- 网络连接失败
- HTTP状态码错误
- JSON解析错误
- 用户未选择任务

### 后端错误处理
- 数据库查询失败
- 任务不存在 (404)
- 并发限制超限
- 进程启动失败
- 数据库更新失败

### 爬虫错误处理
- 网络连接超时
- HTTP状态码错误
- 页面解析失败
- 反爬机制触发

## 性能考虑

1. **并发控制**: 限制同时运行的任务数量
2. **资源管理**: 及时清理已完成的任务进程
3. **内存优化**: 避免长时间运行的任务占用过多内存
4. **错误恢复**: 失败任务的重试机制

## 调试建议

1. **查看浏览器控制台**: 检查JavaScript错误和网络请求
2. **查看后端日志**: 检查Flask应用的输出日志
3. **检查数据库状态**: 验证任务状态是否正确更新
4. **测试Scrapy独立运行**: 验证爬虫本身是否能正常工作