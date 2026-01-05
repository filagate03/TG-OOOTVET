# Gunicorn configuration file for deployment
import os

# Server socket
bind = "127.0.0.1:8000"  # Beget typically uses port 8000 for Python apps, binding to localhost for security
workers = 2  # Number of worker processes
worker_class = "uvicorn.workers.UvicornWorker"  # Use uvicorn worker for FastAPI
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "tg_otvet_api"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190