#!/usr/bin/env python
import logging
from time import sleep

from lib.commands import commands
from lib.websocket import registry
from lib.config import CONFIG
from lib.modules import folder_import

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s│%(levelname)-4.4s│%(name)s ⇒ %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler(),  # Also print to console
    ],
)
log = logging.getLogger(__name__)

modules = folder_import("./modules")

def main():
    server1 = registry.register_server(
        CONFIG["websocket"]["listen"]["host"],
        CONFIG["websocket"]["listen"]["port"]
    )
    server1.set_handler(commands.loop)
    while True:
        sleep(5)



if __name__ == "__main__":
    main()
