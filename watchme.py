import sys
import time

from prefect import flow, get_run_logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


@flow
def on_file_changed(path: str):
    get_run_logger().info(f"{path!r} has changed")


class PrefectEventHandler(FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent):
        on_file_changed(path=event.src_path)

    def on_closed(self, event: FileSystemEvent):
        on_file_changed(path=event.src_path)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"start watching directory {path!r}")
    event_handler = PrefectEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
