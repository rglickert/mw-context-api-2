from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import subprocess
import time

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script_to_run):
        self.script_to_run = script_to_run
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(["python", self.script_to_run])

    def on_modified(self, event):
        if event.src_path.endswith("main.py"):
            self.start_script()

if __name__ == "__main__":
    script = "main.py"
    event_handler = ReloadHandler(script)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
