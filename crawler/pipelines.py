import json
from itemadapter import ItemAdapter
import logging

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('items.json', 'w')
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"[Pipeline] Opening JSON writer for spider: {spider.name}")

    def close_spider(self, spider):
        self.file.close()
        self.logger.info(f"[Pipeline] Closing JSON writer for spider: {spider.name}")

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.logger.info(f"[Pipeline] Written item to JSON: {item}")
        return item

class DatabasePipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None

    def open_spider(self, spider):
        try:
            from app import db
            from models.job import CrawlResult
            self.db = db
            self.CrawlResult = CrawlResult
            self.logger.info(f"[Pipeline] Opening database connection for spider: {spider.name}")
        except Exception as e:
            self.logger.error(f"[Pipeline] Failed to initialize DB in pipeline: {e}")
            self.db = None
            self.CrawlResult = None

    def close_spider(self, spider):
        self.logger.info(f"[Pipeline] Closing database connection for spider: {spider.name}")

    def process_item(self, item, spider):
        if not hasattr(self, 'db') or self.db is None or self.CrawlResult is None:
            self.logger.warning("[Pipeline] DB not initialized; skipping DB save")
            return item

        try:
            adapter = ItemAdapter(item)
            scraped_data = json.dumps(adapter.asdict(), ensure_ascii=False)
            title = adapter.get('title')
            content = adapter.get('content')
            url = adapter.get('url')
            job_id = adapter.get('job_id')
            run_id = adapter.get('run_id')

            result = self.CrawlResult(
                job_id=job_id if job_id is not None else 0,
                run_id=run_id,
                url=url or '',
                title=title,
                content=content,
                scraped_data=scraped_data
            )

            self.db.session.add(result)
            self.db.session.commit()
            self.logger.info(f"[Pipeline] Saved item to database (job_id={job_id}, run_id={run_id}, url={url})")
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"[Pipeline] Error saving item to database: {e}")
        return item