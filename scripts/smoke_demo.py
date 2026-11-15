"""Start two owned localhost processes; verify UI proxy and API using synthetic data."""

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    processes = []
    try:
        commands = [
            [
                str(ROOT / ".venv/bin/python"),
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--no-access-log",
            ],
            ["npm", "--prefix", "frontend", "run", "dev", "--", "--host", "127.0.0.1"],
        ]
        for command in commands:
            processes.append(
                subprocess.Popen(
                    command,
                    cwd=ROOT,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
        targets = [
            ("http://127.0.0.1:8000/api/v1/health", "health"),
            ("http://127.0.0.1:5173/clinical", "html"),
            ("http://127.0.0.1:5173/api/v1/episodes", "episodes"),
            (
                "http://127.0.0.1:5173/api/v1/episodes/synthetic-progressor?cutoff_hour=32",
                "episode",
            ),
        ]
        for url, kind in targets:
            for _ in range(60):
                if any(p.poll() is not None for p in processes):
                    raise RuntimeError("A demo server failed to start; inspect occupied ports")
                try:
                    with urlopen(url, timeout=1) as response:
                        content = response.read()
                        assert response.status == 200
                        if kind == "health":
                            assert json.loads(content)["model_available"] is False
                        if kind == "episodes":
                            assert len(json.loads(content)["episodes"]) == 5
                        if kind == "episode":
                            data = json.loads(content)
                            assert data["outcome"]["state"] == "progressed"
                            assert data["prediction"]["probability"] is None
                        print(f"PASS: {kind}")
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("Demo service did not start")
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)


if __name__ == "__main__":
    main()
