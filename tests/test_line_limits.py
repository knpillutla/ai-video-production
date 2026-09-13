"""Architecture enforcement test: hard 300-line limit per file across src/."""

from pathlib import Path


def test_no_file_exceeds_300_lines():
    """Verify that every single Python file in src/ does not exceed 300 lines."""
    src_dir = Path(__file__).resolve().parent.parent / "src"
    violations = []

    for py_file in src_dir.rglob("*.py"):
        line_count = len(py_file.read_text(encoding="utf-8").splitlines())
        if line_count > 300:
            violations.append(f"{py_file.name} ({line_count} lines)")

    assert not violations, f"Hard 300-line ceiling violated by: {', '.join(violations)}"
