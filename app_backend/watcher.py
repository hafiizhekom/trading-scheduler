import os
from watchfiles import run_process

if __name__ == '__main__':
    print("[WATCHER] Auto-reload mode ON. Watching for changes in 'app/'...")
    os.environ["PYTHONPATH"] = "."
    run_process('app', target='uvicorn app.main:app --host 0.0.0.0 --port 8000')
