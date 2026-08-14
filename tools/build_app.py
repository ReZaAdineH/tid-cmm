"""Build the single-file guided TID-CMM assessment tool."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_tool_data import build as build_data  # noqa: E402

def build(out: Path) -> Path:
    data = build_data()
    out.parent.mkdir(parents=True, exist_ok=True)
    # Written as a file as well as embedded: build_site.py reads it to publish the
    # ATT&CK technique index at /api/techniques.json.
    (ROOT / "build" / "tool_data.json").write_text(
        json.dumps(data, separators=(",", ":"), ensure_ascii=False))
    html = (ROOT / "tools" / "app_template.html").read_text()
    html = html.replace("/*__DATA__*/", json.dumps(data, separators=(",", ":"), ensure_ascii=False))
    assert "__DATA__" not in html
    out.write_text(html)
    return out

if __name__ == "__main__":
    p = build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "tid-cmm-assessment.html")
    print(f"{p}  ({p.stat().st_size/1024:.0f} KB)")
