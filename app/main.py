import os
import yaml
import logging
import logging.config

from dotenv import load_dotenv

from watcher import Watcher
from config import WATCH_FOLDER, OUTPUT_FOLDER

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'logging_config.yml')

with open(config_path, 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

load_dotenv(override=True)

if __name__ == "__main__":
    logger.debug('Start the program')

    logger.debug('WATCH_FOLDER: %s', WATCH_FOLDER)
    logger.debug('OUTPUT_FOLDER: %s', OUTPUT_FOLDER)

    watcher = Watcher()
    watcher.start()