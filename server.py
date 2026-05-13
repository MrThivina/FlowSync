"""Compatibility launcher for FlowSync POS.

The available backend in this workspace is the dependency-free Node.js server
in server.js. Run it with:

    node server.js
"""

from pathlib import Path
import subprocess


if __name__ == "__main__":
    subprocess.run(["node", str(Path(__file__).with_name("server.js"))], check=True)
