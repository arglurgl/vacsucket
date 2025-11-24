#!/usr/bin/env python
import json

from libs.globals import project_root

# This file might be used for config validation

with open(project_root / "config.json", "r") as file_fd:
    CONFIG = json.load(file_fd)
