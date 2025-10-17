"""
Gunicorn configuration file.

For more configuration options see:
https://docs.gunicorn.org/en/stable/settings.html
"""

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 1  # For async workers, usually 1-2 workers is enough
worker_class = "aiohttp.GunicornWebWorker"

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "qorpo-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Worker timeouts
timeout = 30
graceful_timeout = 30
keepalive = 2

# Server hooks for debugging
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Gunicorn is starting")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Gunicorn is reloading")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn is ready. Spawning workers")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized")

def worker_int(worker):
    """Called when a worker received the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received SIGINT/SIGQUIT")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Gunicorn is shutting down")
