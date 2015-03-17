import logging
from app.ssddp import SSDDP

logging.basicConfig(
    format="{levelname:<8} {name:>30}:{funcName:<20}: {message}",
    style='{',
    level=logging.DEBUG,
)

if __name__ == "__main__":
    app = SSDDP("[Node01]")
    app.start()
