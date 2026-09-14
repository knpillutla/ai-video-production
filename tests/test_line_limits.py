"""Architecture enforcement test: hard 300-line limit per file across src/."""

from pathlib import Path


def test_no_file_exceeds_300_lines():
    """Verify that every single code, template, style, and script file in src/ is <= 300 lines."""
    src_dir = Path(__file__).resolve().parent.parent / "src"
    violations = []

    valid_extensions = {".py", ".html", ".css", ".js", ".json"}
    for file_path in src_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in valid_extensions:
            line_count = len(file_path.read_text(encoding="utf-8").splitlines())
            if line_count > 300:
                violations.append(f"{file_path.relative_to(src_dir)} ({line_count} lines)")

    assert not violations, f"Hard 300-line ceiling violated by: {', '.join(violations)}"
