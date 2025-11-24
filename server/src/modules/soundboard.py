"""
Soundboard module using ffplay backend (from ffmpeg).

Requirements:
    sudo apt install ffmpeg

No GUI dependencies. No Python audio libraries needed.
"""

import os
import subprocess as sp
from pathlib import Path

import lib.modules as m
from lib.config import CONFIG

CONFIG = CONFIG["modules"]["soundboard"]


class Soundboard:
    def __init__(self):
        self.processes: list = []
        self.allow_overlap: bool = True
        self.media_dir: Path = Path(CONFIG["media_dir"]).resolve()
        self.__cheese_msg: str = "Common srly? Bee xcellent to each other!"


    def prepend_media_dir(self, path: Path = Path("")):
        m.log.info("prepend_media_dir: media_dir " + str(self.media_dir))
        m.log.info("prepend_media_dir: got " + str(path) + " initially")

        target = (self.media_dir / path).resolve()
        m.log.info("prepend_media_dir: target is " + str(target))

        try:
            target.relative_to(self.media_dir)
        except ValueError as err:
            m.log.warning(err)
            m.log.warning("Someone tried to cheese with path: " + str(path))
            raise err

        return target


    def toggle_overlap(self):
        self.allow_overlap = not self.allow_overlap


    def play_sound(self, filepath: Path):
        try:
            filepath = self.prepend_media_dir(filepath)
        except ValueError:
            return self.__cheese_msg

        if not os.path.exists(filepath):
            error_msg = f"Error: File not found: {filepath}"
            log.error(error_msg)
            return error_msg

        if not self.allow_overlap:
            self.stop_last(0)
 
        m.log.info("play_sound: trying to play " + str(filepath))
        proc = sp.Popen(
            ["ffplay", "-nodisp", "-autoexit", filepath],
            stdout=sp.DEVNULL,
            stderr=sp.DEVNULL,
        )
        self.processes.append(proc)
        return "played: " + str(filepath)


    def stop_last(self, number_of_processes=0):
        self.processes = [p for p in self.processes if p.poll() is None]

        if number_of_processes == 0:
            # Stop all
            for proc in self.processes:
                proc.terminate()
                proc.wait()
            self.processes = []
        else:
            # Stop last N processes
            to_stop = self.processes[-number_of_processes:]
            for proc in to_stop:
                proc.terminate()
                proc.wait()
            self.processes = self.processes[:-number_of_processes]


    def is_playing(self):
        self.processes = [p for p in self.processes if p.poll() is None]
        return len(self.processes) > 0


    def list_sounds(self, directory: Path=Path("/")):
        # TODO: change type to dict and make directory available {"name": "hello-world.txt", "type": "<file or dir>"}
        directory = self.prepend_media_dir(directory)
        if not os.path.exists(directory):
            print(f"Error: Directory not found: {directory}")
            return []

        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue

            # Use ffprobe to detect if it's an audio file
            result = sp.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "a:0",
                    "-show_entries",
                    "stream=codec_type",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    filepath,
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout.strip() == "audio":
                files.append(filename)

        return files




S = Soundboard()
def sound(parameter):
    m.log.info("Got echo parameter: " + parameter)
    parameter_split = parameter.split(maxsplit=1)
    if len(parameter_split) == 1:
        sub_command = parameter
        sub_parameter = ""
    elif len(parameter_split) >= 2:
        sub_command, sub_parameter = parameter_split
    else:
        m.log.warning("split is proably 0; how?!: " + parameter)
        return "You did something i hoped i already catched. An empty string as command"


    match sub_command:
        case "p":
            return S.play_sound(Path(sub_parameter))
        case "l":
            return S.list_sounds(Path(sub_parameter))
        case _:
            log_message = "Recieved unkown sub_command and parameter: " + parameter
            m.log.warning(log_message)
            return log_message

m.register("a", sound)
