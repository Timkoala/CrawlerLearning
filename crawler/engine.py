import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import sys
from multiprocessing import Process, Queue
import time
from crawler.spiders.custom_spider import CustomSpider
import logging

# Configure logging for the engine
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class CrawlerEngine:
    def __init__(self):
        self.processes = {}
        self.results = {}
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
    def start_crawl(self, job_id, target_url, max_depth, custom_rules=None, settings=None):
        """Start a crawl job in a separate process"""
        self.logger.info(f"[Engine] Starting crawl job {job_id} for URL: {target_url}")
        
        if job_id in self.processes:
            raise ValueError(f"Job {job_id} is already running")
            
        # Create a queue for communication
        result_queue = Queue()
        
        # Initialize Flask app context to create a run record
        run_id = None
        try:
            from app import create_app, db
            from models.job import CrawlRun
            flask_app = create_app()
            with flask_app.app_context():
                run = CrawlRun(job_id=job_id, status='running', max_depth=int(max_depth))
                db.session.add(run)
                db.session.commit()
                run_id = run.id
                self.logger.info(f"[Engine] Created run {run_id} for job {job_id}")
        except Exception as e:
            self.logger.error(f"[Engine] Failed to create run for job {job_id}: {e}")
        
        # Start the crawl in a separate process
        process = Process(target=self._run_spider, args=(job_id, run_id, target_url, max_depth, custom_rules, settings, result_queue))
        process.start()
        
        self.logger.info(f"[Engine] Started process for job {job_id} with PID: {process.pid}")
        
        # Store process info
        self.processes[job_id] = {
            'process': process,
            'start_time': time.time(),
            'result_queue': result_queue,
            'run_id': run_id
        }
        
        return job_id
    
    def _run_spider(self, job_id, run_id, target_url, max_depth, custom_rules, settings, result_queue):
        """Run the spider in a separate process"""
        try:
            # Configure logging for the spider process
            logging.basicConfig(
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"[Engine] Process started for job {job_id}")
            
            # Initialize Flask app context in this process so SQLAlchemy works in pipelines
            flask_app = None
            try:
                from app import create_app
                flask_app = create_app()
                app_ctx = flask_app.app_context()
                app_ctx.push()
                self.logger.info("[Engine] Flask app context pushed in spider process")
            except Exception as e:
                self.logger.error(f"[Engine] Failed to initialize Flask app context: {e}")
            
            # Configure Scrapy settings
            scrapy_settings = get_project_settings()
            if settings:
                for key, value in settings.items():
                    scrapy_settings.set(key, value)
            
            # Add logging settings
            scrapy_settings.set('LOG_LEVEL', 'INFO')
            
            self.logger.info(f"[Engine] Configured Scrapy settings for job {job_id}")
            
            # Create and start the crawler process
            process = CrawlerProcess(scrapy_settings)
            process.crawl(CustomSpider, job_id=job_id, run_id=run_id, target_url=target_url, max_depth=max_depth, custom_rules=custom_rules, name=f'spider_{job_id}')
            
            self.logger.info(f"[Engine] Starting crawl process for job {job_id}")
            process.start()
            
            self.logger.info(f"[Engine] Crawl process finished for job {job_id}")
            
            # Update run status to completed
            try:
                if flask_app and run_id:
                    from app import db
                    from models.job import CrawlRun
                    with flask_app.app_context():
                        run = db.session.get(CrawlRun, run_id)
                        if run:
                            run.status = 'completed'
                            run.ended_at = __import__('datetime').datetime.utcnow()
                            db.session.commit()
            except Exception as e:
                self.logger.error(f"[Engine] Failed to update run status: {e}")
            
            # Send success message
            result_queue.put(('success', f'Job {job_id} completed successfully'))
        except Exception as e:
            self.logger.error(f"[Engine] Error in job {job_id}: {str(e)}")
            # Update run to failed
            try:
                if 'flask_app' in locals() and flask_app and run_id:
                    from app import db
                    from models.job import CrawlRun
                    with flask_app.app_context():
                        run = db.session.get(CrawlRun, run_id)
                        if run:
                            run.status = 'failed'
                            run.ended_at = __import__('datetime').datetime.utcnow()
                            db.session.commit()
            except Exception:
                pass
            # Send error message
            result_queue.put(('error', str(e)))
        finally:
            # Pop Flask app context if it was pushed
            try:
                if 'app_ctx' in locals():
                    app_ctx.pop()
            except Exception:
                pass
    
    def stop_crawl(self, job_id):
        """Stop a running crawl job"""
        self.logger.info(f"[Engine] Stopping crawl job {job_id}")
        
        if job_id not in self.processes:
            raise ValueError(f"Job {job_id} is not running")
            
        process = self.processes[job_id]['process']
        if process.is_alive():
            process.terminate()
            process.join()
            
        # Update run status to stopped
        run_id = self.processes[job_id].get('run_id')
        try:
            from app import create_app, db
            from models.job import CrawlRun
            flask_app = create_app()
            with flask_app.app_context():
                if run_id:
                    run = db.session.get(CrawlRun, run_id)
                    if run:
                        run.status = 'stopped'
                        run.ended_at = __import__('datetime').datetime.utcnow()
                        db.session.commit()
        except Exception:
            pass
        
        del self.processes[job_id]
        
    def get_job_status(self, job_id):
        """Get the status of a crawl job"""
        if job_id not in self.processes:
            return 'not_found'
            
        process = self.processes[job_id]['process']
        if process.is_alive():
            self.logger.info(f"[Engine] Job {job_id} is still running")
            return 'running'
        else:
            # Check if there are results
            result_queue = self.processes[job_id]['result_queue']
            if not result_queue.empty():
                result = result_queue.get()
                self.results[job_id] = result
                self.logger.info(f"[Engine] Job {job_id} completed with result: {result}")
                # Clean up
                del self.processes[job_id]
                return 'completed'
            self.logger.info(f"[Engine] Job {job_id} finished but no results yet")
            return 'finished'
            
    def get_all_jobs(self):
        """Get status of all jobs"""
        jobs = {}
        for job_id in list(self.processes.keys()):
            jobs[job_id] = self.get_job_status(job_id)
        return jobs