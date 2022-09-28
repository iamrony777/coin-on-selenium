import logging
from os import makedirs
from rich.logging import RichHandler
from dotenv import load_dotenv

FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")

load_dotenv(".env")
makedirs("screenshot", exist_ok=True)