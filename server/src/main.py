#!/usr/bin/env python
import logging
from pathlib import Path
from time import sleep

from libs.commands import commands
from libs.websocket import registry
from libs.config import CONFIG
from libs.modules import folder_import
from libs.globals import project_root

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s│%(levelname)-4.4s│%(name)s ⇒ %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler(),  # Also print to console
    ],
)
log = logging.getLogger(__name__)

modules = folder_import(project_root / Path("modules"))

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
