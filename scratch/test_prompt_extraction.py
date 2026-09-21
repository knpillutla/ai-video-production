import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.agents.classifier_agent import classifier_agent

p1 = "romantic telugu dance video in telangana dialect in village atmosphere"
p2 = "10 sec romantic telugu dance video in telangana dialect in village atmosphere"
print("P1 Overrides:", classifier_agent.extract_prompt_overrides(p1))
print("P1 Detected:", classifier_agent.detect(p1))
print("P2 Overrides:", classifier_agent.extract_prompt_overrides(p2))
