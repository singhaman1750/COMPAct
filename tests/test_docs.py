"""The README and docs stay in step with the code: commands use real gearbox types and motors,
every gearbox type is listed, and links to repo files point to files that exist."""
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import gearbox_runner  # noqa: E402
from CommonComponents import load_motor  # noqa: E402

DOCS = [REPO_ROOT / "README.md", REPO_ROOT / "tests" / "README.md", *sorted((REPO_ROOT / "docs").glob("*.md"))]


def doc_id(path):
    return path.relative_to(REPO_ROOT).as_posix()


def commands(text):
    """(gb_type, motor, material) for every actOpt.py command and every gearbox-table example row."""
    found = []
    for line in text.splitlines():
        if "actOpt.py" in line and "--gb_type" in line:
            gb = re.search(r"--gb_type\s+(\S+)", line)
            motor = re.search(r"--motor\s+(\S+)", line)
            material = re.search(r"--material\s+(\S+)", line)
            if gb and motor and not gb.group(1).startswith("<") and not motor.group(1).startswith("<"):
                found.append((gb.group(1), motor.group(1), material.group(1) if material else "3dp"))
        row = re.match(r"\|\s*`(\w+)`\s*\|.*\|\s*`--motor (\w+) --gr [\d.]+`\s*\|", line)
        if row:
            found.append((row.group(1), row.group(2), "3dp"))
    return found


@pytest.mark.parametrize("path", DOCS, ids=doc_id)
def test_commands_use_real_gearbox_types_and_motors(path):
    for gb_type, motor, material in commands(path.read_text(encoding="utf-8")):
        assert gb_type in gearbox_runner.GEARBOXES, f"unknown --gb_type {gb_type}"
        assert material in gearbox_runner.MATERIAL_MODES, f"unknown --material {material}"
        load_motor(motor, motor_type=gearbox_runner.GEARBOXES[gb_type].motor_type)


def test_readme_lists_every_gearbox_type():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"^\|\s*`(\w+)`\s*\|", text, re.M))
    assert set(gearbox_runner.GEARBOXES) <= listed, set(gearbox_runner.GEARBOXES) - listed


@pytest.mark.parametrize("path", DOCS, ids=doc_id)
def test_links_to_repo_files_exist(path):
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue  # web links and in-page anchors
        file_part = target.split("#")[0]
        assert (path.parent / file_part).exists(), f"{doc_id(path)} links to missing {target}"
