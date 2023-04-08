import logging
from os import makedirs
from rich.logging import RichHandler
from dotenv import load_dotenv

makedirs("screenshot", exist_ok=True)
makedirs("logs", exist_ok=True)
makedirs("cache", exist_ok=True)

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(), logging.FileHandler("logs/coin-in-selenium.log")]
)
log = logging.getLogger("rich")

load_dotenv(".env")
