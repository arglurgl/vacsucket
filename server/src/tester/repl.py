#!/usr/bin/env python

import code
import readline
import sys
from websockets.sync.client import connect, ClientConnection

websocket: ClientConnection
__last_address: str = ""

def connections():
    global websocket
    global __last_address

    if __last_address:
        websocket = connect(__last_address)
        print(">>> connected with last address, restart to go through all of them again")
        return

    connections = [
        "ws://192.168.13.230:8765",
        "ws://localhost:8765"
    ]
    for address in connections:
        try:
            websocket = connect(address)
            __last_address = address
            return
        except Exception as err:
            global error
            print(address, err)
    print(">>> None worked")
    sys.exit(1)



def send(message):
    try:
        websocket.send(message)
    except Exception as err:
        print(">>> error:" , err)
        print(">>> connecting again and trying to send again")
        connections()
        websocket.send(message)

    print(">>> Command send")
    message = websocket.recv()
    print(f"Received: {message}")


class CustomConsole(code.InteractiveConsole):
    def runsource(self, source, filename="<input>", symbol="single"):
        # catch if commanmd without parameter
        parameter = ""
        try:
            command, parameter = source.split(maxsplit=1)
        except ValueError:
            command = ""

        if command:
            match command:
                case "s":
                    if len(parameter) == 0:
                        raise ValueError("s command needs a parameter")
                    send("s " + parameter)
                case "commands":
                    commands()
                case _:
                    print(">>> arbitrary command")
                    send(command + " " + parameter)
        else:
           # Otherwise, treat as normal Python code
           return super().runsource(source, filename, symbol)

        readline.add_history(source)
        return False


def commands():
    print("Right now only `s` is implemented")
    print("Try `s <parameter`")


def main():
    console = CustomConsole()
    try:
        console.interact(
            banner='This is a "patched" python repl. Try `commands` to see what can be done'
        )
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    connections()
    main()
