"""Run both local servers: python -m scripts.run_local."""

import importlib.util
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def main():
    if importlib.util.find_spec("uvicorn") is None:
        print(
            "Install dependencies: python -m pip install -r requirements.txt"
        )
        return 1
    for port in (8000, 5500):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                print(
                    f"Port {port} is already in use; stop that server first."
                )
                return 1

    commands = [
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        [
            sys.executable,
            "-m",
            "http.server",
            "5500",
            "--bind",
            "127.0.0.1",
            "--directory",
            str(ROOT_DIR / "frontend"),
        ],
    ]
    processes = []
    try:
        for command in commands:
            processes.append(subprocess.Popen(command, cwd=ROOT_DIR))
        print("Web: http://localhost:5500/", flush=True)
        print("Swagger: http://127.0.0.1:8000/docs", flush=True)
        print(
            "Keep this terminal open. Ctrl+C stops both servers.", flush=True
        )
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
        print("A server stopped; check its error output above.")
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
