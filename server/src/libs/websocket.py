from websockets.asyncio.server import serve, ServerConnection
import asyncio
import logging
import threading
from typing import Callable, Awaitable

log = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self, host: str, port: int, loop: asyncio.AbstractEventLoop):
        """
        Initialize WebSocket manager.

        Args:
            host: Host address to bind to
            port: Port number to bind to
            loop: Event loop to run the server on
        """
        self.host = host
        self.port = port
        self.loop = loop
        self.handler: Callable[[ServerConnection], Awaitable[None]] | None = None

    def set_handler(self, handler: Callable[[ServerConnection], Awaitable[None]]):
        """
        Set the handler for websocket connections.
        Server will start automatically.

        Args:
            handler: Async function that handles websocket connections.
        """
        self.handler = handler
        log.info(f"Handler set for WebSocket manager on {self.host}:{self.port}")
        asyncio.run_coroutine_threadsafe(self._run(), self.loop)
        log.info(f"Started WebSocket server on {self.host}:{self.port}")

    async def handle_connection(self, websocket: ServerConnection):
        """Handle a single websocket connection with error handling"""
        try:
            await self.handler(websocket)
        except Exception as e:
            log.error(f"Error in websocket handler: {e}")
        finally:
            try:
                log.error("Trying to close websocket after error ...")
                await websocket.close()
                log.error("... closed!")
            except Exception as e:
                log.error(f"Error closing websocket: {e}")

    async def _run(self):
        """
        Start the WebSocket server listening.
        """
        log.info(f"WebSocket server listening on {self.host}:{self.port}")

        async with serve(
            self.handle_connection,
            self.host,
            self.port,
        ) as server:
            await server.serve_forever()


class WebSocketManagerRegistry:
    """Registry for managing multiple WebSocket servers"""
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.__servers: dict[str, WebSocketManager] = {}
        self.__loop = loop

    def register_server(self, host: str, port: int) -> WebSocketManager:
        """
        Register a server by host and port.
        Returns the manager so you can set its handler.

        Args:
            host: Host address
            port: Port number

        Returns:
            WebSocketManager instance

        Example:
            server = registry.register_server("0.0.0.0", 8765)
            server.set_handler(my_handler)
        """
        key = f"{host}:{port}"

        if key in self.__servers:
            log.warning(f"Server {key} is already registered, returning existing manager")
            return self.__servers[key]

        manager = WebSocketManager(host, port, self.__loop)
        self.__servers[key] = manager
        log.info(f"Registered server {host}:{port}")

        return manager

    def get(self, host: str, port: int) -> WebSocketManager | None:
        """
        Retrieve a registered server by host and port.

        Args:
            host: Host address
            port: Port number

        Returns:
            WebSocketManager instance or None if not found
        """
        key = f"{host}:{port}"
        return self.__servers.get(key)

    def list_servers(self) -> list[str]:
        """List all registered server addresses"""
        return list(self.__servers.keys())


def _run_event_loop(loop: asyncio.AbstractEventLoop):
    """Internal: Run the event loop forever in a background thread"""
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Create event loop and start it in background thread
_loop = asyncio.new_event_loop()
_thread = threading.Thread(target=_run_event_loop, args=(_loop,), daemon=True)
_thread.start()

# Global registry instance - import this from other modules
registry = WebSocketManagerRegistry(_loop)
