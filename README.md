# Vacsucket

Vacsucket is a remote control and video streaming system for a vacuum robot, inspired by Mars rover teleoperation. It allows you to control the robot's movement, stream live video, and interact with modules such as soundboard via a web interface or command line tools. The robot is controlled via an Arduino board receiving serial command and emulating its IR remote. The robot used is an unmodified GB Life MY-549A vacuum cleaner robot.

## Features
- Web-based control panel for robot movement (WASD/arrow keys, buttons)
- Live webcam streaming via WebRTC
- Modular server architecture (Python)
- IR remote bridge (Arduino/PlatformIO)
- Soundboard module (play audio remotely)
- Command-line tester tools (REPL, WASD)

## Project Structure
```
vacsucket/
├── client/web/         # Web UI: control panel, webcam
├── ir_serial_bridge/   # Arduino code for IR remote bridge
├── server/             # Python server: WebSocket, modules, config
│   ├── src/modules/    # Modules: ir_remote, soundboard, webcam, echo
│   ├── src/tester/     # Command-line tools: repl.py, wasd.py
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/yourusername/vacsucket.git
cd vacsucket
```

### 2. Server Setup (Python)
- Install dependencies see pyproject.toml or flake.nix for hints.
- Start server via `python main.py`

### 3. IR Serial Bridge (Arduino)
- Install [PlatformIO](https://platformio.org/)
- Open `ir_serial_bridge` in PlatformIO and upload to your board (e.g., Arduino Uno or Pro Mini)

### 4. Web Client
- Open `client/web/index.html` in your browser
- Ensure server and IR bridge are running and accessible

## Usage
- Control the robot via the web interface (WASD, arrow keys, or buttons)
- View live video from the robot's webcam
- Use soundboard and other modules via the web or command line
- Command-line tools: run `server/src/tester/repl.py` or `wasd.py` for direct control


## License
GPL v3
