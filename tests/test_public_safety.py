import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".csv", ".txt", ".ipynb"}


def test_readme_and_expected_public_artifacts_exist():
    expected = [
        "README.md",
        "analysis/01_process_sensor_stability.ipynb",
        "analysis/02_deposition_parameter_analysis.ipynb",
        "data/process_sensor_summary.csv",
        "data/deposition_condition_summary.csv",
        "data/wafer_uniformity_sample.csv",
        "images/sensor_stability_by_run.png",
        "images/gas_flow_vs_thickness.png",
        "images/process_condition_variation.png",
        "images/wafer_uniformity_map.png",
    ]
    assert [name for name in expected if not (ROOT / name).is_file()] == []


def test_public_files_contain_no_private_identifiers_or_credentials():
    forbidden = [
        re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        re.compile(r"01[016789]-?\d{3,4}-?\d{4}"),
        re.compile("C:" + re.escape("\\") + re.escape("Users"), re.IGNORECASE),
        re.compile("user" + "_pw", re.IGNORECASE),
        re.compile("pass" + "word\\s*=", re.IGNORECASE),
        re.compile("jwy" + "oo", re.IGNORECASE),
    ]
    violations = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if ".git" in path.parts or ".pytest_cache" in path.parts or "test_public_safety.py" == path.name:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in forbidden:
            if pattern.search(text):
                violations.append(f"{path.relative_to(ROOT)} matched {pattern.pattern}")
    assert violations == []


def test_notebooks_are_valid_json_and_have_no_execution_errors():
    errors = []
    for path in (ROOT / "analysis").glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for cell in notebook.get("cells", []):
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    errors.append(f"{path.name}: {output.get('ename')}")
    assert errors == []
