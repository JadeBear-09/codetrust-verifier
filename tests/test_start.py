from __future__ import annotations

import subprocess

import start


def test_uv_environment_uses_python_module_runner(monkeypatch):
    commands = []
    monkeypatch.setattr(start.shutil, "which", lambda name: "/tools/uv")
    monkeypatch.setattr(
        start,
        "_run",
        lambda command, check=True: commands.append(command)
        or subprocess.CompletedProcess(command, 0),
    )

    runner = start._prepare_environment(development=True)

    assert commands == [["/tools/uv", "sync", "--extra", "dev"]]
    assert runner == ["/tools/uv", "run", "python", "-m"]


def test_setup_accepts_intentional_block_verdict(monkeypatch):
    commands = []
    monkeypatch.setattr(start, "_prepare_environment", lambda development: ["python", "-m"])
    monkeypatch.setattr(
        start,
        "_run",
        lambda command, check=True: commands.append(command)
        or subprocess.CompletedProcess(command, 1),
    )

    result = start.main(["--setup-only", "--no-open"])

    assert result == 0
    assert commands[0][2:4] == ["codetrust.cli", "verify"]


def test_start_reuses_running_codetrust(monkeypatch):
    commands = []
    monkeypatch.setattr(start, "_prepare_environment", lambda development: ["python", "-m"])
    monkeypatch.setattr(start, "_codetrust_running", lambda url: True)
    monkeypatch.setattr(
        start,
        "_run",
        lambda command, check=True: commands.append(command)
        or subprocess.CompletedProcess(command, 1),
    )

    result = start.main(["--no-open"])

    assert result == 0
    assert len(commands) == 1
    assert commands[0][2:4] == ["codetrust.cli", "verify"]
