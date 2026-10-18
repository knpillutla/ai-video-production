from pathlib import Path
import json
import re

content_path = Path(r"C:\Users\Krishna Pillutla\.gemini\antigravity-ide\brain\b4039830-1adc-4ae1-9450-353648d74680\.system_generated\steps\2467\content.md")
text = content_path.read_text(encoding="utf-8", errors="ignore")

# Find title tag or videoDetails
for m in re.finditer(r'"title":\s*"([^"]+)"', text):
    val = m.group(1)
    if "YouTube" not in val and len(val) > 3:
        print("Title candidate:", val)
        break

for m in re.finditer(r'"author":\s*"([^"]+)"', text):
    print("Author:", m.group(1))
    break

for m in re.finditer(r'"shortDescription":\s*"([^"]+)"', text):
    print("Description:", m.group(1)[:200])
    break
