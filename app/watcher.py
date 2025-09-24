import os
import time
import logging
import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta
from config import WATCH_FOLDER, OUTPUT_FOLDER
from file_processor import FileProcessor

class Watcher:

    @property
    def logger(self):
        # Create a logger specific to this class
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def start(self):
        self.logger.debug("Watcher started...")
        self.logger.debug("🔁 Polling folder: %s", WATCH_FOLDER)

        seen_files = dict()
        last_file_time = None
        merge_wait_seconds = 30
        merge_performed = False

        while True:
            new_file_found = self.poll_folder(WATCH_FOLDER, seen_files)
        
            if new_file_found:
                last_file_time = datetime.now()
                merge_performed = False

            if (
                not new_file_found
                and last_file_time is not None
                and not merge_performed
                and datetime.now() - last_file_time > timedelta(seconds=merge_wait_seconds)
            ):
                self.logger.debug("🕒 No new files for 30s — starting merge.")
                self.merge_files()
                merge_performed = True
 
            time.sleep(2)    

    def poll_folder(self, path: Path, seen: dict) -> bool:
        new_file_found = False
        for file in path.glob("*.xls*"):
            if file.is_file():
                mtime = file.stat().st_mtime
                if file not in seen or seen[file] != mtime:
                    seen[file] = mtime
                    self.logger.debug("📦 New or updated file detected: %s", file.name)
                    self.handle_file(file)
                    new_file_found = True
        return new_file_found
    

    def merge_files(self):
        try:
            files = [f for f in OUTPUT_FOLDER.glob("*.xlsx") if not f.name.startswith("~$") and not f.name.startswith("merged_")]
            if not files:
                self.logger.debug("⚠️ No files found for merging.")
                return

            merged = pd.DataFrame()

            for i, file in enumerate(files):
                self.logger.debug("📄 Reading: %s", file.name)
                try:
                    df = pd.read_excel(file)
                    merged = df if i == 0 else pd.concat([merged, df], ignore_index=True)

                    #Delete the file after succesful read
                    file.unlink()
                    self.logger.debug("🗑️ Deleted source file: %s", file.name)

                except Exception as e:
                    self.logger.error("❌ Error reading %s", file.name, exc_info=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_FOLDER / f"merged_{timestamp}.xlsx"
            merged.to_excel(output_path, index=False)
            self.logger.debug("✅ Merged %d files into: %s", len(files), output_path.name)
        except Exception as e:
            self.logger.debug("❌ Merge failed: %s", e, exc_info=True)

    def handle_file(self, path: Path):
        file_processor = FileProcessor()
        try:
            if path.suffix.lower() == ".xls":
                self.logger.debug("📥 Detected .xls file: %s", path.name)

                converted = self.convert_to_xlsx(path, WATCH_FOLDER)
                if converted:
                    file_processor.process_file(converted)
                    path.unlink()
            elif path.suffix.lower() == ".xlsx":
                self.logger.debug("📥 Detected .xlsx file: %s", path.name)
                file_processor.process_file(path)
            else:
                self.logger.debug("❌ Unsupported file type: %s", path.name)
        except Exception as e:
            self.logger.error("❌ Error processing file %s: %s", {path.name}, e, exc_info=True)

    def convert_to_xlsx(self, input_path: Path, output_folder: Path):
        try:
            tables = pd.read_html(input_path)
            if not tables:
                self.logger.debug("❌ No tables found in %s", input_path.name)
                return None
        
            df = tables[0]
            # Set the first row as header
            df.columns = df.iloc[0]
            df = df[1:]  # drop the old header row
            df.reset_index(drop=True, inplace=True)
    
            # Optional: strip column names
            df.columns = df.columns.str.strip()
    
            output_path = output_folder / (input_path.stem + ".xlsx")
            df.to_excel(output_path, index=False)
            self.logger.debug("🔁 Converted %s to %s", input_path.name, output_path.name)
            return output_path
        except Exception as e:
            self.logger.error("❌ Failed to convert %s: %s", input_path.name, e, exc_info=True)
            return None