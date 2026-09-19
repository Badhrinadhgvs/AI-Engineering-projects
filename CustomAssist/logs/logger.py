import logging

logging.basicConfig(
    filemode="a",
    filename="logs/app.log",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    force=True,  # <-- clears existing handlers and reapplies this config
)
logging.info("Hi there")
