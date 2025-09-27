#!/usr/bin/env python3

import multiprocessing
import os
from gunicorn.glogging import Logger as GunicornLogger
from pvgisprototype.log import initialize_web_api_logger, logger
from pvgisprototype.core.caching import clear_request_caches
import gc


class StubbedGunicornLogger(GunicornLogger):
    def setup(self, cfg):
        super().setup(cfg)
        for handler in self.error_log.handlers[:]:
            self.error_log.removeHandler(handler)
        self.error_log.propagate = True
        logger.debug("StubbedGunicornLogger initialized")


def post_request(worker, req, environ, resp):
    """Clear caches after each request to prevent memory leaks"""
    clear_request_caches()
    gc.collect()


def worker_exit(server, worker):
    """Clean up when worker exits"""
    clear_request_caches()
    gc.collect()


def on_starting(server):
    """Called just before the master process is initialized"""
    logger.info(f"Starting Gunicorn master process (PID: {os.getpid()})")


def when_ready(server):
    """Called just after the server is started"""
    logger.info(f"Gunicorn is ready. Listening at: {server.address}")


def worker_int(worker):
    """Called when worker receives SIGINT or SIGQUIT signal"""
    logger.info(f"Worker {worker.pid} received interrupt signal")


def pre_fork(server, worker):
    """Called just before a worker is forked"""
    logger.debug(f"About to fork worker {worker.age}")


def post_fork(server, worker):
    """Called just after a worker has been forked"""
    logger.info(f"Worker {worker.pid} forked successfully")


# Initialize logging
initialize_web_api_logger(server="gunicorn")

# Basic server settings
bind = "127.0.0.2:8000"
workers = max(2, multiprocessing.cpu_count() - 2)  # Leave at least 2 cores free
worker_class = "uvicorn.workers.UvicornWorker"

# Performance settings for high load (10k requests)
worker_connections = 1000  # Max concurrent connections per worker
max_requests = 1000  # Restart workers after this many requests
max_requests_jitter = 100  # Add randomness to worker restart
timeout = 30  # Increased for complex PVGIS calculations
keepalive = 5  # Keep connections alive for reuse

# Memory management
preload_app = False  # Safer for Redis caching, prevents shared state issues
max_worker_memory = 2048  # MB - restart worker if it exceeds this

# Threading (for I/O operations like Redis, file access)
threads = 4  # Increased for I/O-heavy PVGIS operations

# Logging
logger_class = StubbedGunicornLogger
errorlog = "-"  # Log to stdout
accesslog = None  # Disable access logs for performance
capture_output = True
enable_stdio_inheritance = True

# Security
limit_request_line = 8192  # Max HTTP request line size
limit_request_fields = 200  # Max number of header fields
limit_request_field_size = 8192  # Max size of header field

# Process naming
proc_name = "pvgis-web-api"

# Graceful handling
graceful_timeout = 120  # Time to wait for workers to finish during shutdown
user = None  # Run as current user
group = None  # Run as current group

# TMP directory for worker processes
tmp_upload_dir = "/tmp"

# SSL/TLS (if needed in production)
# keyfile = None
# certfile = None
