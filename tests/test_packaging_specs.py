"""Tests for packaging spec regressions."""

from __future__ import annotations

import ast
from pathlib import Path


def test_linux_pyinstaller_spec_uses_exclude_binaries_for_onedir_build() -> None:
    spec_path = (
        Path(__file__).resolve().parents[1]
        / "packaging"
        / "pyinstaller"
        / "playlistforge.linux.spec"
    )

    module = ast.parse(spec_path.read_text(encoding="utf-8"))

    exe_call = None
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "exe" for target in node.targets
        ):
            exe_call = node.value
            break

    assert isinstance(exe_call, ast.Call)
    assert isinstance(exe_call.func, ast.Name)
    assert exe_call.func.id == "EXE"

    exclude_binaries = {
        keyword.arg: keyword.value for keyword in exe_call.keywords if keyword.arg is not None
    }["exclude_binaries"]
    assert isinstance(exclude_binaries, ast.Constant)
    assert exclude_binaries.value is True
