import psutil
import time
from crawler.engine import CrawlerEngine
import json
import logging

class ProcessManager:
    def __init__(self):
        self.engine = CrawlerEngine()
        self.max_concurrent_jobs = 5  # Limit concurrent jobs
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
    def start_job(self, job_id, target_url, max_depth=1, custom_rules=None):
        """Start a crawl job"""
        self.logger.info(f"[ProcessManager] Starting job {job_id} for URL: {target_url}")
        
        # Check if we can start a new job
        if len(self.engine.processes) >= self.max_concurrent_jobs:
            raise Exception("Maximum concurrent jobs reached")
            
        # Create spider settings
        settings = {
            'MAX_DEPTH': max_depth,
            'DEPTH_LIMIT': int(max_depth)
        }
        
        # Parse custom rules if they exist
        parsed_custom_rules = None
        if custom_rules:
            try:
                if isinstance(custom_rules, str):
                    parsed_custom_rules = json.loads(custom_rules)
                else:
                    parsed_custom_rules = custom_rules
            except:
                parsed_custom_rules = None
        
        self.logger.info(f"[ProcessManager] Job {job_id} settings - Max depth: {max_depth}")
        
        # Start the crawl with the predefined spider class
        result = self.engine.start_crawl(job_id, target_url, max_depth, parsed_custom_rules, settings)
        self.logger.info(f"[ProcessManager] Job {job_id} started successfully")
        return result
        
    def stop_job(self, job_id):
        """Stop a crawl job"""
        self.logger.info(f"[ProcessManager] Stopping job {job_id}")
        return self.engine.stop_crawl(job_id)
        
    def get_job_status(self, job_id):
        """Get status of a specific job"""
        status = self.engine.get_job_status(job_id)
        self.logger.info(f"[ProcessManager] Job {job_id} status: {status}")
        return status
        
    def get_all_jobs(self):
        """Get status of all jobs"""
        jobs = self.engine.get_all_jobs()
        self.logger.info(f"[ProcessManager] All jobs status: {jobs}")
        return jobs
        
    def get_system_stats(self):
        """Get system statistics"""
        stats = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'active_jobs': len(self.engine.processes)
        }
        self.logger.info(f"[ProcessManager] System stats: {stats}")
        return stats