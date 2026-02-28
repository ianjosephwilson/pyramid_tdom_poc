import os
import multiprocessing
from glob import glob

PORT = os.environ["PORT"]

accesslog = "-"
errorlog = "-"
workers = 2  # multiprocessing.cpu_count() * 2 + 1
preload_app = False
wsgi_app = "pyramid_tdom_poc:main()"
loglevel = "INFO"
bind = f"[::]:{PORT}"

if os.environ.get("GUNICORN_RELOADING_ARGS", ""):
    reload = True
    reload_extra_files = sum(
        [glob(entry) for entry in os.environ.get("GUNICORN_RELOADING_ARGS").split(",")],
        [],
    )
