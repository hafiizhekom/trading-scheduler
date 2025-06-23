import os
from watchfiles import run_process

if __name__ == '__main__':
    print("[WATCHER] Auto-reload mode ON. Watching for changes in 'app/'...")
    os.environ["PYTHONPATH"] = "."  # ← tambahkan ini
    run_process('app', target='python app/main.py')
