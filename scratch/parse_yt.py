import re
from pathlib import Path

path = Path(r"C:\Users\Krishna Pillutla\.gemini\antigravity-ide\brain\76531dd4-8df0-4238-95f7-78cacbc65050\.system_generated\steps\2199\content.md")
text = path.read_text(encoding="utf-8", errors="ignore")

patterns = [
    r'"videoDetails":\{"videoId":"([^"]+)","title":"([^"]+)"',
    r'"title":"([^"]+)"',
    r'<title>([^<]+)</title>',
    r'<meta name="title" content="([^"]+)"',
    r'<meta property="og:title" content="([^"]+)"',
    r'"author":"([^"]+)"',
    r'"ownerChannelName":"([^"]+)"',
    r'"description":"([^"]+)"',
]

for p in patterns:
    matches = list(re.finditer(p, text))
    if matches:
        print(f"Pattern {p}:")
        for m in matches[:5]:
            print("  ", m.groups())
