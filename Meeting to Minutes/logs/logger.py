import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="w",
    datefmt="%Y-%m-%d %H:%M:%S",
)
