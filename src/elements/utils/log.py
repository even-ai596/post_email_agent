import logging
import os
import time

DEFAULT_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"

# Set log level based on environment
log_level = logging.INFO if os.environ.get("ENV", "dev") == "dev" else logging.INFO

# Configure the root logger
logging.basicConfig(
    format=DEFAULT_LOG_FORMAT,
    level=log_level,
)

# Create and configure our module logger
logger = logging.getLogger(__name__)


logger.info("Hello, World!")
try:
    1 / 0
except Exception as e:
    logger.exception(e)
print(getattr(logging, "_levelToName"))
try:
    time.sleep(10)
except KeyboardInterrupt as e:
    logger.exception(e)