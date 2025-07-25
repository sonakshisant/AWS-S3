import os
import shutil
from datetime import datetime
import logging

# ==== DEBUGGING SETUP ====
print("=== DEBUG MODE ===")
logging.basicConfig(
    level=logging.DEBUG,  # More detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_organizer.log', mode='w'),  # Overwrite log each run
        logging.StreamHandler()
    ]
)

# ==== CONFIGURATION ====
SUPPORTED_EXT = {'.pdf', '.jpeg', '.jpg', '.mp4', '.doc', '.docx', '.txt'}
files = [f for f in os.listdir('.') if os.path.isfile(f)]
logging.info(f"ALL FILES IN FOLDER: {files}")

supported_files = [f for f in files if os.path.splitext(f)[1].lower() in SUPPORTED_EXT]
logging.info(f"SUPPORTED FILES: {supported_files}")

# ==== PROCESS FILES ====
for file in supported_files:
    try:
        print(f"\nProcessing: {file}")
        mod_time = os.path.getmtime(file)
        date_folder = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
        print(f"Modification time: {mod_time} → Folder: {date_folder}")

        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
            logging.info(f"Created folder: {date_folder}")
        
        shutil.move(file, os.path.join(date_folder, file))
        logging.info(f"Moved: {file} → {date_folder}/")
        print(f"Moved '{file}' to '{date_folder}'")

    except Exception as e:
        logging.error(f"FAILED: {file} ({str(e)})")
        print(f"Error: {e}")

print("\n=== Script finished ===")
logging.info("------ END ------")