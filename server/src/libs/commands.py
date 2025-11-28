#!/usr/bin/env python
import logging
from typing import Any, Callable, Coroutine
from websockets.asyncio.server import ServerConnection
from asyncio import iscoroutine

log = logging.getLogger(__name__)


class Commands(dict):
    def __init__(self) -> None:
        super().__init__()
        self.__websocket: ServerConnection

    async def unkown(self, message):
        log_message = "Recieved unkown message: " + message
        log.warning(log_message)
        return await self.__websocket.send(log_message)

    CommandReturn = str | list | dict | None
    def register(
            self,
            command: str,
            function: Callable[[str], CommandReturn | Coroutine[Any, Any, CommandReturn]]
        ):
        log.info("Registering new command: " + command)
        self[command] = {
            "function": function,
            "name": function.__name__,
            "description:": function.__doc__
        }

    async def loop(self, websocket: ServerConnection):
        self.__websocket = websocket
        async for message in websocket:
            log.info("Recieved: " + str(message))

            # catch if command without parameter
            parsed = message.split(maxsplit=1)
            match len(parsed):
                case 2:
                    command, parameter = parsed
                case 1:
                    log.debug("Recieved command without parameter")
                    command, parameter = parsed[0], ""
                case _:
                    log.debug("This should be impossible with ''.split(maxsplit=1)")
                    raise ValueError("message was split to many times")

            # check if command is regestered
            if command in self:
                # support async and normal functions
                result = self[command]["function"](parameter)
                if iscoroutine(result):
                    result = await result
                await websocket.send(result)
            else:
                await self.unkown(message)

commands = Commands()
