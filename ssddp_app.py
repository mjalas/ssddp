import logging
from app.ssddp import SSDDP

logging.basicConfig(
    format="{levelname:<8} {name:>30}:{funcName:<20}: {message}",
    style='{',
    level=logging.DEBUG,
)

if __name__ == "__main__":
    service_list_file = "static_node_messages/service_list.json"
    app = SSDDP(None, None, None, False, service_list_file)
    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()
        print("User interruption occurred!\nEnding program!")