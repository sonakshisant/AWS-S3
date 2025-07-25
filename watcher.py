import os
import time
import zipfile
import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Environment vars
WATCH_DIR = os.getenv("WATCH_DIR", "./watched_dir")
ZIP_NAME = "upload_bundle.zip"
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_PREFIX = "uploads/"

# S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# Compress changed files
def zip_files(file_list, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for file in file_list:
            arcname = os.path.relpath(file, WATCH_DIR)
            zipf.write(file, arcname=arcname)

# Upload to S3
def upload_to_s3(file_path):
    key = f"{S3_PREFIX}{os.path.basename(file_path)}"
    s3.upload_file(file_path, BUCKET_NAME, key)
    print(f"[✔] Uploaded to S3: s3://{BUCKET_NAME}/{key}")

# Watcher handler
class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.modified_files = set()

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[!] Modified: {event.src_path}")
            self.modified_files.add(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            print(f"[+] New file: {event.src_path}")
            self.modified_files.add(event.src_path)

# Main loop
def start_monitoring():
    if not os.path.exists(WATCH_DIR):
        print(f"[ERROR] Watched directory '{WATCH_DIR}' does not exist.")
        return

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=True)
    observer.start()

    print(f"[INFO] Watching directory: {WATCH_DIR}")

    try:
        while True:
            time.sleep(10)
            if event_handler.modified_files:
                print("[INFO] Changes detected. Zipping and uploading...")
                zip_files(event_handler.modified_files, ZIP_NAME)
                upload_to_s3(ZIP_NAME)
                event_handler.modified_files.clear()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()
