import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "app.log"
LOG_DIR.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filemode="a",
    filename=str(LOG_DIR),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    force=True,  # <-- clears existing handlers and reapplies this config
)
logging.info("Hi there")
