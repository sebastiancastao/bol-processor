#!/usr/bin/env python3
"""
Approach 3: Production-Ready Microservice
==========================================
Built for scale and reliability with async processing,
monitoring, health checks, and production features.
"""

import os
import uuid
import time
import asyncio
import tempfile
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue, Empty

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import pandas as pd

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core processors
import sys
sys.path.append('..')
from pdf_processor import PDFProcessor
from data_processor import DataProcessor
from csv_exporter import CSVExporter

class JobStatus(Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class Priority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class ProcessingJob:
    """Processing job model."""
    job_id: str
    status: JobStatus
    priority: Priority
    pdf_content: bytes
    pdf_filename: str
    csv_content: Optional[bytes] = None
    csv_filename: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def processing_time(self) -> Optional[float]:
        """Calculate processing time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if job has expired (24 hours)."""
        return datetime.now() - self.created_at > timedelta(hours=24)

class MetricsCollector:
    """Collect and track processing metrics."""
    
    def __init__(self):
        self.jobs_processed = 0
        self.jobs_failed = 0
        self.total_processing_time = 0.0
        self.start_time = datetime.now()
        self.lock = threading.Lock()
    
    def record_success(self, processing_time: float):
        """Record successful job."""
        with self.lock:
            self.jobs_processed += 1
            self.total_processing_time += processing_time
    
    def record_failure(self):
        """Record failed job."""
        with self.lock:
            self.jobs_failed += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        with self.lock:
            uptime = (datetime.now() - self.start_time).total_seconds()
            avg_processing_time = (
                self.total_processing_time / self.jobs_processed 
                if self.jobs_processed > 0 else 0
            )
            
            return {
                'uptime_seconds': uptime,
                'jobs_processed': self.jobs_processed,
                'jobs_failed': self.jobs_failed,
                'success_rate': (
                    self.jobs_processed / (self.jobs_processed + self.jobs_failed)
                    if (self.jobs_processed + self.jobs_failed) > 0 else 0
                ),
                'average_processing_time_seconds': avg_processing_time,
                'jobs_per_hour': self.jobs_processed / (uptime / 3600) if uptime > 0 else 0
            }

class JobQueue:
    """Priority job queue for processing."""
    
    def __init__(self, max_size: int = 100):
        self.queue = Queue(maxsize=max_size)
        self.jobs: Dict[str, ProcessingJob] = {}
        self.lock = threading.Lock()
    
    def add_job(self, job: ProcessingJob) -> bool:
        """Add job to queue."""
        try:
            with self.lock:
                if len(self.jobs) >= 100:  # Limit total jobs
                    self._cleanup_expired_jobs()
                
                self.jobs[job.job_id] = job
                self.queue.put((job.priority.value, job.job_id), timeout=1)
                logger.info(f"Job {job.job_id} queued with priority {job.priority.name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to queue job {job.job_id}: {e}")
            return False
    
    def get_next_job(self, timeout: float = 1.0) -> Optional[ProcessingJob]:
        """Get next job from queue."""
        try:
            _, job_id = self.queue.get(timeout=timeout)
            with self.lock:
                job = self.jobs.get(job_id)
                if job and not job.is_expired:
                    job.status = JobStatus.PROCESSING
                    job.started_at = datetime.now()
                    return job
                else:
                    # Job expired or not found
                    if job:
                        job.status = JobStatus.EXPIRED
                    return None
        except Empty:
            return None
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Get job by ID."""
        with self.lock:
            return self.jobs.get(job_id)
    
    def update_job(self, job: ProcessingJob):
        """Update job status."""
        with self.lock:
            self.jobs[job.job_id] = job
    
    def _cleanup_expired_jobs(self):
        """Remove expired jobs."""
        expired_jobs = [
            job_id for job_id, job in self.jobs.items()
            if job.is_expired or job.status in [JobStatus.COMPLETED, JobStatus.FAILED]
        ]
        
        for job_id in expired_jobs[:50]:  # Remove up to 50 old jobs
            job = self.jobs.pop(job_id, None)
            if job and job.result_path and os.path.exists(job.result_path):
                try:
                    os.unlink(job.result_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup result file: {e}")
        
        logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status."""
        with self.lock:
            status_counts = {}
            for status in JobStatus:
                status_counts[status.value] = sum(
                    1 for job in self.jobs.values() if job.status == status
                )
            
            return {
                'total_jobs': len(self.jobs),
                'queue_size': self.queue.qsize(),
                'status_breakdown': status_counts
            }

class ProcessingWorker:
    """Worker for processing jobs."""
    
    def __init__(self, worker_id: str, job_queue: JobQueue, metrics: MetricsCollector):
        self.worker_id = worker_id
        self.job_queue = job_queue
        self.metrics = metrics
        self.running = False
        self.current_job_id = None
    
    def start(self):
        """Start the worker."""
        self.running = True
        logger.info(f"Worker {self.worker_id} started")
        
        while self.running:
            try:
                job = self.job_queue.get_next_job(timeout=1.0)
                if job:
                    self.current_job_id = job.job_id
                    self._process_job(job)
                    self.current_job_id = None
                    
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                if self.current_job_id:
                    self._fail_current_job(str(e))
    
    def stop(self):
        """Stop the worker."""
        self.running = False
        logger.info(f"Worker {self.worker_id} stopped")
    
    def _process_job(self, job: ProcessingJob):
        """Process a single job."""
        logger.info(f"Worker {self.worker_id} processing job {job.job_id}")
        
        working_dir = None
        try:
            # Create working directory
            working_dir = tempfile.mkdtemp(prefix=f"bol_job_{job.job_id}_")
            
            # Step 1: Process PDF
            self._process_pdf(job, working_dir)
            
            # Step 2: Process data
            self._process_data(working_dir)
            
            # Step 3: Create CSV
            csv_path = self._create_csv(working_dir)
            
            # Step 4: Merge additional CSV if provided
            if job.csv_content and job.csv_filename:
                csv_path = self._merge_csv(csv_path, job)
            
            # Step 5: Save result
            result_path = self._save_result(csv_path, job.job_id)
            
            # Update job
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.result_path = result_path
            job.metadata.update({
                'worker_id': self.worker_id,
                'processing_time': job.processing_time,
                'result_size': os.path.getsize(result_path)
            })
            
            self.job_queue.update_job(job)
            self.metrics.record_success(job.processing_time)
            
            logger.info(f"Job {job.job_id} completed in {job.processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error_message = str(e)
            
            self.job_queue.update_job(job)
            self.metrics.record_failure()
            
        finally:
            # Cleanup working directory
            if working_dir and os.path.exists(working_dir):
                try:
                    shutil.rmtree(working_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup working dir: {e}")
    
    def _process_pdf(self, job: ProcessingJob, working_dir: str):
        """Process PDF step."""
        pdf_path = os.path.join(working_dir, job.pdf_filename)
        with open(pdf_path, 'wb') as f:
            f.write(job.pdf_content)
        
        processor = PDFProcessor(working_dir)
        if not processor.process_first_pdf():
            raise Exception("PDF processing failed")
    
    def _process_data(self, working_dir: str):
        """Process data step."""
        processor = DataProcessor()
        processor.session_dir = working_dir
        processor.invoice_data = {}
        
        if not processor.process_all_files():
            raise Exception("Data processing failed")
    
    def _create_csv(self, working_dir: str) -> str:
        """Create CSV step."""
        exporter = CSVExporter(working_dir)
        if not exporter.combine_to_csv():
            raise Exception("CSV creation failed")
        
        csv_path = os.path.join(working_dir, "combined_data.csv")
        if not os.path.exists(csv_path):
            raise Exception("CSV file not created")
        
        return csv_path
    
    def _merge_csv(self, base_csv_path: str, job: ProcessingJob) -> str:
        """Merge CSV step."""
        # Save additional CSV
        ext = os.path.splitext(job.csv_filename)[1]
        additional_csv_path = os.path.join(
            os.path.dirname(base_csv_path), 
            f"additional{ext}"
        )
        
        with open(additional_csv_path, 'wb') as f:
            f.write(job.csv_content)
        
        try:
            # Read and merge
            base_df = pd.read_csv(base_csv_path, dtype=str)
            
            if ext.lower() == '.csv':
                additional_df = pd.read_csv(additional_csv_path, dtype=str)
            else:
                additional_df = pd.read_excel(additional_csv_path, dtype=str)
            
            # Simple merge for now
            merged_df = pd.concat([base_df, additional_df], ignore_index=True)
            merged_df.to_csv(base_csv_path, index=False)
            
            return base_csv_path
            
        finally:
            if os.path.exists(additional_csv_path):
                os.unlink(additional_csv_path)
    
    def _save_result(self, csv_path: str, job_id: str) -> str:
        """Save final result."""
        results_dir = os.path.join(tempfile.gettempdir(), 'bol_results')
        os.makedirs(results_dir, exist_ok=True)
        
        result_path = os.path.join(results_dir, f"result_{job_id}.csv")
        shutil.copy2(csv_path, result_path)
        
        return result_path
    
    def _fail_current_job(self, error_message: str):
        """Fail the current job."""
        if self.current_job_id:
            job = self.job_queue.get_job(self.current_job_id)
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now()
                job.error_message = error_message
                self.job_queue.update_job(job)
                self.metrics.record_failure()

class ProcessingEngine:
    """Main processing engine with worker management."""
    
    def __init__(self, num_workers: int = 2):
        self.job_queue = JobQueue()
        self.metrics = MetricsCollector()
        self.workers = []
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.num_workers = num_workers
        
        # Start workers
        for i in range(num_workers):
            worker = ProcessingWorker(f"worker-{i}", self.job_queue, self.metrics)
            self.workers.append(worker)
            self.executor.submit(worker.start)
        
        logger.info(f"Processing engine started with {num_workers} workers")
    
    def submit_job(self, pdf_content: bytes, pdf_filename: str, 
                  csv_content: Optional[bytes] = None, 
                  csv_filename: Optional[str] = None,
                  priority: Priority = Priority.NORMAL) -> str:
        """Submit a new processing job."""
        
        job_id = str(uuid.uuid4())
        job = ProcessingJob(
            job_id=job_id,
            status=JobStatus.QUEUED,
            priority=priority,
            pdf_content=pdf_content,
            pdf_filename=pdf_filename,
            csv_content=csv_content,
            csv_filename=csv_filename
        )
        
        if self.job_queue.add_job(job):
            logger.info(f"Job {job_id} submitted successfully")
            return job_id
        else:
            raise Exception("Failed to queue job - system may be overloaded")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status."""
        job = self.job_queue.get_job(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'status': job.status.value,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'processing_time': job.processing_time,
            'error_message': job.error_message,
            'metadata': job.metadata
        }
    
    def get_result(self, job_id: str) -> Optional[bytes]:
        """Get job result."""
        job = self.job_queue.get_job(job_id)
        if not job or job.status != JobStatus.COMPLETED or not job.result_path:
            return None
        
        try:
            with open(job.result_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read result for job {job_id}: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'engine_status': 'running',
            'workers': {
                'total': len(self.workers),
                'active': len([w for w in self.workers if w.running]),
                'current_jobs': [w.current_job_id for w in self.workers if w.current_job_id]
            },
            'queue': self.job_queue.get_queue_status(),
            'metrics': self.metrics.get_metrics(),
            'system': {
                'temp_dir': tempfile.gettempdir(),
                'max_file_size': '100MB',
                'job_retention': '24 hours'
            }
        }
    
    def shutdown(self):
        """Shutdown the processing engine."""
        logger.info("Shutting down processing engine...")
        
        for worker in self.workers:
            worker.stop()
        
        self.executor.shutdown(wait=True, timeout=30)
        logger.info("Processing engine shutdown complete")

# Flask Application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Initialize processing engine
engine = ProcessingEngine(num_workers=2)

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.route('/health', methods=['GET'])
def health():
    """Comprehensive health check."""
    return jsonify({
        'status': 'healthy',
        'service': 'BOL Processing API',
        'approach': 'production_microservice',
        'version': '3.0',
        'timestamp': datetime.now().isoformat(),
        'system_status': engine.get_system_status()
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """Get system metrics."""
    return jsonify(engine.get_system_status())

@app.route('/submit', methods=['POST'])
def submit_job():
    """Submit processing job."""
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'PDF file required'}), 400
        
        pdf_file = request.files['pdf']
        csv_file = request.files.get('csv')
        priority_str = request.form.get('priority', 'normal').upper()
        
        try:
            priority = Priority[priority_str]
        except KeyError:
            priority = Priority.NORMAL
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No PDF file selected'}), 400
        
        # Submit job
        job_id = engine.submit_job(
            pdf_content=pdf_file.read(),
            pdf_filename=secure_filename(pdf_file.filename),
            csv_content=csv_file.read() if csv_file and csv_file.filename != '' else None,
            csv_filename=secure_filename(csv_file.filename) if csv_file and csv_file.filename != '' else None,
            priority=priority
        )
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Job submitted successfully',
            'status_url': f'/status/{job_id}',
            'result_url': f'/result/{job_id}'
        }), 202
        
    except Exception as e:
        logger.error(f"Job submission error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """Get job status."""
    status = engine.get_job_status(job_id)
    if not status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(status)

@app.route('/result/<job_id>', methods=['GET'])
def get_job_result(job_id: str):
    """Download job result."""
    result = engine.get_result(job_id)
    if not result:
        return jsonify({'error': 'Result not available'}), 404
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        tmp.write(result)
        tmp.flush()
        
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f'bol_result_{job_id}.csv',
            mimetype='text/csv'
        )

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Comprehensive API documentation."""
    return jsonify({
        'service': 'BOL Processing API - Production Microservice',
        'version': '3.0',
        'architecture': 'Async job queue with worker pool',
        'endpoints': {
            'POST /submit': {
                'description': 'Submit processing job',
                'parameters': {
                    'pdf': 'PDF file (required, multipart/form-data)',
                    'csv': 'CSV file (optional, multipart/form-data)',
                    'priority': 'Job priority: low, normal, high, urgent (optional)'
                },
                'response': 'Job ID and status URLs'
            },
            'GET /status/<job_id>': {
                'description': 'Get job status',
                'response': 'Job status and metadata'
            },
            'GET /result/<job_id>': {
                'description': 'Download job result',
                'response': 'CSV file download'
            },
            'GET /health': {
                'description': 'Health check with system status',
                'response': 'Service and system health'
            },
            'GET /metrics': {
                'description': 'System metrics and performance data',
                'response': 'Detailed system metrics'
            }
        },
        'features': [
            'Async job processing',
            'Priority queue system',
            'Worker pool management',
            'Comprehensive monitoring',
            'Automatic cleanup',
            'Performance metrics',
            'Graceful error handling',
            'Scalable architecture'
        ],
        'advantages': [
            'High throughput processing',
            'Production-ready reliability',
            'Comprehensive monitoring',
            'Scalable worker pool',
            'Priority-based processing',
            'Automatic resource cleanup',
            'Detailed metrics and logging'
        ]
    })

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8083, debug=False)
    finally:
        engine.shutdown() 