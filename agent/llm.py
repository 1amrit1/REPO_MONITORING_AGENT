import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
from groq import Groq

from models.schemas import IssueClassification

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You triage GitHub issues. Classify the issue and respond with JSON matching "
    'this schema: {"type": "bug"|"feature"|"question", "priority": "high"|"med"|"low", '
    '"summary": "<one sentence>"}. If the issue is ambiguous, classify it as "question" '
    "with priority \"low\" and say why in the summary."
)


def _client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set — copy .env.example to .env and add your key")
    return Groq(api_key=api_key)


def classify_issue(title: str, body: str) -> dict:
    response = _client().chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Title: {title}\n\nBody: {body}"},
        ],
    )
    raw = response.choices[0].message.content
    return IssueClassification.model_validate(json.loads(raw)).model_dump()


if __name__ == "__main__":
    result = classify_issue(
        title="App crashes on startup after upgrading to v2.3",
        body="Since updating, the app throws a NullPointerException on launch. "
        "Happens on every device I've tested. Downgrading to v2.2 fixes it.",
    )
    print(json.dumps(result, indent=2))
