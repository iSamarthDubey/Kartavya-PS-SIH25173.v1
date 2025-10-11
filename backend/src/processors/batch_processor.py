"""
Batch Processing Engine
High-performance batch processing for large-scale SIEM data ingestion and analysis
"""

import os
import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Union, AsyncIterator, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from pathlib import Path

# External dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """Batch processing configuration"""
    batch_size: int = 1000
    max_concurrent_batches: int = 10
    timeout_seconds: int = 300
    retry_attempts: int = 3
    checkpoint_interval: int = 100
    
    # Processing options
    enable_compression: bool = True
    enable_deduplication: bool = True
    enable_validation: bool = True
    
    # Storage options
    temp_storage_path: str = "/tmp/batch_processing"
    checkpoint_storage_path: str = "/tmp/checkpoints"
    
    # Performance tuning
    worker_processes: int = mp.cpu_count()
    worker_threads_per_process: int = 4
    memory_limit_mb: int = 1024
    
    # Queue settings
    redis_url: Optional[str] = None
    queue_name: str = "siem_batch_queue"
    priority_queue_name: str = "siem_priority_queue"


@dataclass
class BatchJob:
    """Batch processing job definition"""
    job_id: str
    job_type: str
    source_platform: str
    query: Dict[str, Any]
    data_range: Dict[str, Any]
    
    # Processing options
    processing_options: Dict[str, Any]
    priority: int = 0  # Higher number = higher priority
    
    # Metadata
    created_at: str
    scheduled_for: Optional[str] = None
    estimated_size: Optional[int] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class BatchStatus:
    """Batch processing status"""
    job_id: str
    status: str  # pending, running, completed, failed, cancelled
    progress: float = 0.0
    processed_records: int = 0
    total_records: Optional[int] = None
    
    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_completion: Optional[str] = None
    
    # Results
    output_location: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


class BatchProcessor(ABC):
    """Abstract base class for batch processors"""
    
    @abstractmethod
    async def process_batch(self, data: List[Dict[str, Any]], job: BatchJob) -> List[Dict[str, Any]]:
        """Process a batch of data"""
        pass
    
    @abstractmethod
    async def validate_batch(self, data: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Validate batch data"""
        pass


class SIEMBatchProcessor(BatchProcessor):
    """SIEM-specific batch processor"""
    
    def __init__(self, normalizer=None):
        self.normalizer = normalizer
    
    async def process_batch(self, data: List[Dict[str, Any]], job: BatchJob) -> List[Dict[str, Any]]:
        """Process SIEM data batch"""
        try:
            processed_data = []
            
            for record in data:
                # Normalize data if normalizer available
                if self.normalizer:
                    normalized = self.normalizer.normalize_event(record, job.source_platform)
                    processed_data.append(asdict(normalized))
                else:
                    # Basic processing
                    processed_record = {
                        "timestamp": record.get("timestamp", datetime.now().isoformat()),
                        "source_platform": job.source_platform,
                        "processed_at": datetime.now().isoformat(),
                        "job_id": job.job_id,
                        **record
                    }
                    processed_data.append(processed_record)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            raise
    
    async def validate_batch(self, data: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Validate SIEM batch data"""
        try:
            if not data:
                return False, "Empty batch data"
            
            # Check for required fields
            for i, record in enumerate(data):
                if not isinstance(record, dict):
                    return False, f"Record {i} is not a dictionary"
                
                # Basic validation
                if not record:
                    return False, f"Record {i} is empty"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {e}"


class BatchQueue:
    """High-performance batch processing queue"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.redis_client = None
        self.local_queue = asyncio.Queue()
        self.priority_queue = asyncio.PriorityQueue()
        
    async def initialize(self):
        """Initialize the queue system"""
        if self.config.redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.config.redis_url)
                await self.redis_client.ping()
                logger.info("Connected to Redis for batch queue")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using local queue.")
                self.redis_client = None
        else:
            logger.info("Using local queue for batch processing")
    
    async def enqueue(self, job: BatchJob, priority: bool = False) -> bool:
        """Add job to queue"""
        try:
            job_data = asdict(job)
            
            if self.redis_client:
                # Use Redis queue
                queue_name = self.config.priority_queue_name if priority else self.config.queue_name
                await self.redis_client.lpush(queue_name, json.dumps(job_data))
            else:
                # Use local queue
                if priority:
                    await self.priority_queue.put((job.priority, job))
                else:
                    await self.local_queue.put(job)
            
            logger.info(f"Enqueued job {job.job_id} with priority: {priority}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enqueue job {job.job_id}: {e}")
            return False
    
    async def dequeue(self, priority_first: bool = True) -> Optional[BatchJob]:
        """Get next job from queue"""
        try:
            if self.redis_client:
                # Try priority queue first
                if priority_first:
                    job_data = await self.redis_client.brpop([self.config.priority_queue_name], timeout=1)
                    if not job_data:
                        job_data = await self.redis_client.brpop([self.config.queue_name], timeout=1)
                else:
                    job_data = await self.redis_client.brpop([self.config.queue_name], timeout=1)
                
                if job_data:
                    _, job_json = job_data
                    job_dict = json.loads(job_json)
                    return BatchJob(**job_dict)
            else:
                # Use local queues
                try:
                    if priority_first and not self.priority_queue.empty():
                        _, job = self.priority_queue.get_nowait()
                        return job
                    elif not self.local_queue.empty():
                        return self.local_queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue job: {e}")
            return None
    
    async def get_queue_size(self) -> Dict[str, int]:
        """Get queue sizes"""
        try:
            if self.redis_client:
                normal_size = await self.redis_client.llen(self.config.queue_name)
                priority_size = await self.redis_client.llen(self.config.priority_queue_name)
                return {"normal": normal_size, "priority": priority_size}
            else:
                return {"normal": self.local_queue.qsize(), "priority": self.priority_queue.qsize()}
        except Exception as e:
            logger.error(f"Failed to get queue size: {e}")
            return {"normal": 0, "priority": 0}
    
    async def cleanup(self):
        """Cleanup queue resources"""
        if self.redis_client:
            await self.redis_client.close()


class BatchStatusTracker:
    """Track batch processing status and progress"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.redis_client = None
        self.local_status = {}
        
    async def initialize(self):
        """Initialize status tracking"""
        if self.config.redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.config.redis_url)
                await self.redis_client.ping()
                logger.info("Connected to Redis for status tracking")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using local status tracking.")
                self.redis_client = None
    
    async def update_status(self, job_id: str, status: BatchStatus) -> bool:
        """Update job status"""
        try:
            status_data = asdict(status)
            
            if self.redis_client:
                await self.redis_client.hset(f"batch_status:{job_id}", mapping=status_data)
                # Set expiration (24 hours)
                await self.redis_client.expire(f"batch_status:{job_id}", 86400)
            else:
                self.local_status[job_id] = status_data
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update status for job {job_id}: {e}")
            return False
    
    async def get_status(self, job_id: str) -> Optional[BatchStatus]:
        """Get job status"""
        try:
            if self.redis_client:
                status_data = await self.redis_client.hgetall(f"batch_status:{job_id}")
                if status_data:
                    # Convert bytes to strings if needed
                    status_dict = {k.decode() if isinstance(k, bytes) else k: 
                                 v.decode() if isinstance(v, bytes) else v 
                                 for k, v in status_data.items()}
                    return BatchStatus(**status_dict)
            else:
                status_data = self.local_status.get(job_id)
                if status_data:
                    return BatchStatus(**status_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get status for job {job_id}: {e}")
            return None
    
    async def get_all_statuses(self, limit: int = 100) -> List[BatchStatus]:
        """Get all job statuses"""
        try:
            statuses = []
            
            if self.redis_client:
                # Get all status keys
                keys = await self.redis_client.keys("batch_status:*")
                for key in keys[:limit]:
                    status_data = await self.redis_client.hgetall(key)
                    if status_data:
                        status_dict = {k.decode() if isinstance(k, bytes) else k: 
                                     v.decode() if isinstance(v, bytes) else v 
                                     for k, v in status_data.items()}
                        statuses.append(BatchStatus(**status_dict))
            else:
                for job_id, status_data in list(self.local_status.items())[:limit]:
                    statuses.append(BatchStatus(**status_data))
            
            return statuses
            
        except Exception as e:
            logger.error(f"Failed to get all statuses: {e}")
            return []
    
    async def cleanup_completed(self, older_than_hours: int = 24):
        """Clean up completed job statuses"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            if self.redis_client:
                keys = await self.redis_client.keys("batch_status:*")
                for key in keys:
                    status_data = await self.redis_client.hgetall(key)
                    if status_data:
                        completed_at = status_data.get(b'completed_at' if isinstance(list(status_data.keys())[0], bytes) else 'completed_at')
                        if completed_at:
                            try:
                                completed_time = datetime.fromisoformat(completed_at.decode() if isinstance(completed_at, bytes) else completed_at)
                                if completed_time < cutoff_time:
                                    await self.redis_client.delete(key)
                            except:
                                pass
            else:
                to_remove = []
                for job_id, status_data in self.local_status.items():
                    completed_at = status_data.get('completed_at')
                    if completed_at:
                        try:
                            completed_time = datetime.fromisoformat(completed_at)
                            if completed_time < cutoff_time:
                                to_remove.append(job_id)
                        except:
                            pass
                
                for job_id in to_remove:
                    del self.local_status[job_id]
                    
        except Exception as e:
            logger.error(f"Failed to cleanup completed statuses: {e}")


class BatchExecutionEngine:
    """Main batch processing execution engine"""
    
    def __init__(self, config: BatchConfig, processor: BatchProcessor):
        self.config = config
        self.processor = processor
        self.queue = BatchQueue(config)
        self.status_tracker = BatchStatusTracker(config)
        
        # Execution state
        self.running = False
        self.workers = []
        self.processed_jobs = 0
        self.failed_jobs = 0
        
        # Create directories
        Path(config.temp_storage_path).mkdir(parents=True, exist_ok=True)
        Path(config.checkpoint_storage_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the execution engine"""
        await self.queue.initialize()
        await self.status_tracker.initialize()
        logger.info("Batch execution engine initialized")
    
    async def start(self):
        """Start the batch processing engine"""
        if self.running:
            logger.warning("Batch engine is already running")
            return
        
        self.running = True
        
        # Start worker tasks
        for i in range(self.config.max_concurrent_batches):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Started {len(self.workers)} batch processing workers")
    
    async def stop(self):
        """Stop the batch processing engine"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        # Cleanup resources
        await self.queue.cleanup()
        
        logger.info("Batch processing engine stopped")
    
    async def submit_job(self, job: BatchJob, priority: bool = False) -> bool:
        """Submit a batch job for processing"""
        # Create initial status
        status = BatchStatus(
            job_id=job.job_id,
            status="pending",
            progress=0.0
        )
        
        await self.status_tracker.update_status(job.job_id, status)
        return await self.queue.enqueue(job, priority)
    
    async def get_job_status(self, job_id: str) -> Optional[BatchStatus]:
        """Get status of a specific job"""
        return await self.status_tracker.get_status(job_id)
    
    async def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        queue_sizes = await self.queue.get_queue_size()
        
        return {
            "running": self.running,
            "active_workers": len(self.workers),
            "processed_jobs": self.processed_jobs,
            "failed_jobs": self.failed_jobs,
            "queue_sizes": queue_sizes,
            "success_rate": self.processed_jobs / max(self.processed_jobs + self.failed_jobs, 1) * 100
        }
    
    async def _worker(self, worker_id: str):
        """Worker task for processing jobs"""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get next job
                job = await self.queue.dequeue()
                if not job:
                    await asyncio.sleep(1)  # No jobs available, wait
                    continue
                
                logger.info(f"Worker {worker_id} processing job {job.job_id}")
                await self._process_job(job, worker_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _process_job(self, job: BatchJob, worker_id: str):
        """Process a single batch job"""
        job_id = job.job_id
        
        try:
            # Update status to running
            status = BatchStatus(
                job_id=job_id,
                status="running",
                progress=0.0,
                started_at=datetime.now().isoformat()
            )
            await self.status_tracker.update_status(job_id, status)
            
            # Load or generate data for processing
            data = await self._load_job_data(job)
            
            if not data:
                raise Exception("No data to process")
            
            total_records = len(data)
            status.total_records = total_records
            await self.status_tracker.update_status(job_id, status)
            
            # Process data in chunks
            processed_data = []
            batch_size = self.config.batch_size
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                # Validate batch
                is_valid, validation_error = await self.processor.validate_batch(batch)
                if not is_valid:
                    raise Exception(f"Batch validation failed: {validation_error}")
                
                # Process batch
                processed_batch = await self.processor.process_batch(batch, job)
                processed_data.extend(processed_batch)
                
                # Update progress
                processed_records = min(i + batch_size, total_records)
                progress = (processed_records / total_records) * 100
                
                status.progress = progress
                status.processed_records = processed_records
                await self.status_tracker.update_status(job_id, status)
                
                # Save checkpoint
                if processed_records % (self.config.checkpoint_interval * batch_size) == 0:
                    await self._save_checkpoint(job_id, processed_data)
            
            # Save final results
            output_location = await self._save_results(job_id, processed_data)
            
            # Update final status
            status.status = "completed"
            status.progress = 100.0
            status.completed_at = datetime.now().isoformat()
            status.output_location = output_location
            status.metrics = {
                "total_processed": len(processed_data),
                "processing_time_seconds": (datetime.fromisoformat(status.completed_at) - 
                                          datetime.fromisoformat(status.started_at)).total_seconds()
            }
            
            await self.status_tracker.update_status(job_id, status)
            self.processed_jobs += 1
            
            logger.info(f"Job {job_id} completed successfully by worker {worker_id}")
            
        except Exception as e:
            # Update status to failed
            status = BatchStatus(
                job_id=job_id,
                status="failed",
                error_message=str(e),
                completed_at=datetime.now().isoformat()
            )
            await self.status_tracker.update_status(job_id, status)
            self.failed_jobs += 1
            
            logger.error(f"Job {job_id} failed: {e}")
    
    async def _load_job_data(self, job: BatchJob) -> List[Dict[str, Any]]:
        """Load data for job processing"""
        # This is a placeholder - in real implementation, this would:
        # 1. Connect to SIEM platform using job.source_platform and job.query
        # 2. Execute query to retrieve data
        # 3. Return list of records
        
        # For demo purposes, generate some sample data
        sample_data = []
        for i in range(job.estimated_size or 1000):
            sample_data.append({
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "event_type": f"event_type_{i % 10}",
                "severity": ["low", "medium", "high"][i % 3],
                "message": f"Sample event message {i}",
                "source_ip": f"192.168.1.{i % 255}",
                "destination_ip": f"10.0.0.{i % 255}"
            })
        
        return sample_data
    
    async def _save_checkpoint(self, job_id: str, data: List[Dict[str, Any]]):
        """Save processing checkpoint"""
        try:
            checkpoint_file = Path(self.config.checkpoint_storage_path) / f"{job_id}_checkpoint.json"
            
            with open(checkpoint_file, 'w') as f:
                json.dump(data, f)
                
            logger.debug(f"Saved checkpoint for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint for job {job_id}: {e}")
    
    async def _save_results(self, job_id: str, data: List[Dict[str, Any]]) -> str:
        """Save final processing results"""
        try:
            output_file = Path(self.config.temp_storage_path) / f"{job_id}_results.json"
            
            # Save as JSON
            with open(output_file, 'w') as f:
                json.dump(data, f)
            
            # Also save as CSV if pandas available
            if PANDAS_AVAILABLE:
                try:
                    df = pd.DataFrame(data)
                    csv_file = Path(self.config.temp_storage_path) / f"{job_id}_results.csv"
                    df.to_csv(csv_file, index=False)
                    logger.info(f"Saved results to both JSON and CSV for job {job_id}")
                except Exception as e:
                    logger.warning(f"Failed to save CSV for job {job_id}: {e}")
            
            logger.info(f"Saved results for job {job_id} to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to save results for job {job_id}: {e}")
            raise


class BatchScheduler:
    """Scheduler for batch processing jobs"""
    
    def __init__(self, engine: BatchExecutionEngine):
        self.engine = engine
        self.scheduled_jobs = {}
        self.scheduler_running = False
    
    async def schedule_job(self, job: BatchJob, schedule_time: datetime) -> bool:
        """Schedule a job for future execution"""
        job.scheduled_for = schedule_time.isoformat()
        self.scheduled_jobs[job.job_id] = job
        logger.info(f"Scheduled job {job.job_id} for {schedule_time}")
        return True
    
    async def start_scheduler(self):
        """Start the job scheduler"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        asyncio.create_task(self._scheduler_loop())
        logger.info("Batch scheduler started")
    
    async def stop_scheduler(self):
        """Stop the job scheduler"""
        self.scheduler_running = False
        logger.info("Batch scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                jobs_to_submit = []
                
                for job_id, job in self.scheduled_jobs.items():
                    if job.scheduled_for:
                        scheduled_time = datetime.fromisoformat(job.scheduled_for)
                        if current_time >= scheduled_time:
                            jobs_to_submit.append(job_id)
                
                # Submit ready jobs
                for job_id in jobs_to_submit:
                    job = self.scheduled_jobs.pop(job_id)
                    await self.engine.submit_job(job)
                    logger.info(f"Submitted scheduled job {job_id}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)


# Utility functions
def create_batch_job(
    source_platform: str,
    query: Dict[str, Any],
    job_type: str = "data_ingestion",
    data_range: Optional[Dict[str, Any]] = None,
    **kwargs
) -> BatchJob:
    """Create a batch job with default parameters"""
    
    job_id = str(uuid.uuid4())
    
    return BatchJob(
        job_id=job_id,
        job_type=job_type,
        source_platform=source_platform,
        query=query,
        data_range=data_range or {"start": "now-24h", "end": "now"},
        processing_options=kwargs.get("processing_options", {}),
        priority=kwargs.get("priority", 0),
        created_at=datetime.now().isoformat(),
        scheduled_for=kwargs.get("scheduled_for"),
        estimated_size=kwargs.get("estimated_size"),
        tags=kwargs.get("tags", [])
    )


async def run_batch_system(config: BatchConfig, processor: BatchProcessor):
    """Run the complete batch processing system"""
    
    # Create and initialize engine
    engine = BatchExecutionEngine(config, processor)
    await engine.initialize()
    
    # Create scheduler
    scheduler = BatchScheduler(engine)
    
    try:
        # Start engine and scheduler
        await engine.start()
        await scheduler.start_scheduler()
        
        logger.info("Batch processing system started successfully")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(60)
            
            # Log statistics
            stats = await engine.get_engine_stats()
            logger.info(f"Engine stats: {stats}")
            
    except KeyboardInterrupt:
        logger.info("Shutting down batch processing system")
    finally:
        await scheduler.stop_scheduler()
        await engine.stop()


# Export main classes
__all__ = [
    'BatchConfig',
    'BatchJob',
    'BatchStatus',
    'BatchProcessor',
    'SIEMBatchProcessor',
    'BatchExecutionEngine',
    'BatchScheduler',
    'create_batch_job',
    'run_batch_system'
]
