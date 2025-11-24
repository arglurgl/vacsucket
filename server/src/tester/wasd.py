import sys
import termios
import tty
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


def serial_send(message):
    message = "s " + message
    send(message)


def get_char():
    """Read a single character from stdin."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


def main():
    print("WASD controls active. Press 'q' to quit.")

    while True:
        char = get_char()

        # Check for Ctrl+C (ASCII 3)
        if ord(char) == 3:
            print("\nExiting...")
            break

        match char:
            case "w":
                serial_send("f")
            case "a":
                serial_send("l")
            case "s":
                serial_send("b")
            case "d":
                serial_send("r")

            case "q":
                print("\n\nQuit")
                break
            case _:
                serial_send(char)


if __name__ == "__main__":
    main()
