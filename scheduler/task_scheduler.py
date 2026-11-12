"""
Task Scheduler - Schedules content generation tasks
"""
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskScheduler:
    """
    Scheduler for automated content generation
    Uses schedule library for simple scheduling
    """
    
    def __init__(self, config: dict):
        """
        Initialize scheduler
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.jobs = []
        self.running = False
        
        # Get scheduling configuration
        interval_hours = config.get("CONTENT_INTERVAL_HOURS", 72)  # Default 3 days
        preferred_hour = config.get("PREFERRED_HOUR", 9)
        
        self.interval_hours = interval_hours
        self.preferred_hour = preferred_hour
        
        logger.info(f"Scheduler initialized: {interval_hours}h interval, at {preferred_hour}h")
    
    def schedule_content_job(
        self,
        job_func: Callable,
        job_name: str = "default"
    ):
        """
        Schedule a content generation job
        
        Args:
            job_func: Function to execute
            job_name: Name for this job
        """
        # Run every interval_hours
        job = schedule.every(self.interval_hours).hours.do(job_func)
        job.name = job_name
        
        self.jobs.append(job)
        logger.info(f"Scheduled job '{job_name}': every {self.interval_hours} hours")
    
    def schedule_daily_job(
        self,
        job_func: Callable,
        hour: int = 9,
        minute: int = 0,
        job_name: str = "daily"
    ):
        """
        Schedule a daily job at specific time
        
        Args:
            job_func: Function to execute
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)
            job_name: Name for this job
        """
        job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job_func)
        job.name = job_name
        
        self.jobs.append(job)
        logger.info(f"Scheduled daily job '{job_name}': at {hour:02d}:{minute:02d}")
    
    def schedule_weekly_job(
        self,
        job_func: Callable,
        day_of_week: str,
        hour: int = 9,
        minute: int = 0,
        job_name: str = "weekly"
    ):
        """
        Schedule a weekly job on specific day
        
        Args:
            job_func: Function to execute
            day_of_week: Day name (monday, tuesday, etc.)
            hour: Hour of day
            minute: Minute of hour
            job_name: Name for this job
        """
        job = schedule.every().day_of_week.at(f"{hour:02d}:{minute:02d}").do(job_func)
        job.name = job_name
        
        self.jobs.append(job)
        logger.info(f"Scheduled weekly job '{job_name}': {day_of_week} at {hour:02d}:{minute:02d}")
    
    def start(self):
        """Start the scheduler loop"""
        self.running = True
        logger.info("Starting scheduler...")
        
        # Log scheduled jobs
        for job in self.jobs:
            logger.info(f"  - Job: {job.name}, Next run: {job.next_run}")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Stopping scheduler...")
    
    def get_next_run(self) -> Optional[datetime]:
        """Get the next scheduled run time"""
        if self.jobs:
            return self.jobs[0].next_run
        return None
    
    def clear_jobs(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.jobs = []
        logger.info("All jobs cleared")


class APSchedulerWrapper:
    """
    Advanced scheduler using APScheduler (optional)
    For more complex scheduling needs
    """
    def __init__(self, config: dict):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
            from apscheduler.triggers.cron import CronTrigger
            
            self.Scheduler = BackgroundScheduler
            self.IntervalTrigger = IntervalTrigger
            self.CronTrigger = CronTrigger
            self.available = True
            logger.info("APScheduler available for advanced scheduling")
        except ImportError:
            self.available = False
            logger.warning("APScheduler not available. Install with: pip install APScheduler")
    
    def schedule_interval(
        self,
        job_func: Callable,
        hours: int = 72,
        job_name: str = "interval_job"
    ):
        """Schedule job to run at interval"""
        if not self.available:
            logger.warning("APScheduler not available")
            return None
        
        scheduler = self.Scheduler()
        scheduler.add_job(
            job_func,
            self.IntervalTrigger(hours=hours),
            id=job_name,
            name=job_name,
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"APScheduler scheduled '{job_name}': every {hours} hours")
        return scheduler
    
    def schedule_cron(
        self,
        job_func: Callable,
        cron_expression: str,
        job_name: str = "cron_job"
    ):
        """Schedule job using cron expression"""
        if not self.available:
            logger.warning("APScheduler not available")
            return None
        
        scheduler = self.Scheduler()
        scheduler.add_job(
            job_func,
            self.CronTrigger.from_crontab(cron_expression),
            id=job_name,
            name=job_name,
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"APScheduler scheduled '{job_name}': cron {cron_expression}")
        return scheduler
