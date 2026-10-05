import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

from models.schemas import IssueClassification

load_dotenv()

SYSTEM_PROMPT = (
    "You triage GitHub issues. Classify the issue and respond with JSON matching "
    'this schema: {"type": "bug"|"feature"|"question", "priority": "high"|"med"|"low", '
    '"summary": "<one sentence>"}. If the issue is ambiguous, classify it as "question" '
    "with priority \"low\" and say why in the summary."
)


def _call_groq(title: str, body: str) -> str:
    """api_key type — hosted, needs GROQ_API_KEY."""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set — copy .env.example to .env and add your key")

    model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    response = Groq(api_key=api_key).chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Title: {title}\n\nBody: {body}"},
        ],
    )
    return response.choices[0].message.content


def _call_ollama(title: str, body: str) -> str:
    """local type — no key, needs a running local server with the model pulled."""
    import ollama

    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    try:
        response = ollama.Client(host=host).chat(
            model=model,
            format="json",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Title: {title}\n\nBody: {body}"},
            ],
        )
    except Exception as exc:
        raise RuntimeError(
            f"Could not get a response from Ollama at {host} — is `ollama serve` running, "
            f"and is `{model}` pulled (`ollama pull {model}`)?"
        ) from exc
    return response["message"]["content"]


_CALLERS = {"groq": _call_groq, "ollama": _call_ollama}


def classify_issue(title: str, body: str) -> dict:
    provider = os.environ.get("LLM_PROVIDER", "groq")
    caller = _CALLERS.get(provider)
    if caller is None:
        raise ValueError(f"Unsupported LLM_PROVIDER '{provider}' — choose one of {list(_CALLERS)}")

    raw = caller(title, body)
    return IssueClassification.model_validate(json.loads(raw)).model_dump()


if __name__ == "__main__":
    result = classify_issue(
        title="App crashes on startup after upgrading to v2.3",
        body="Since updating, the app throws a NullPointerException on launch. "
        "Happens on every device I've tested. Downgrading to v2.2 fixes it.",
    )
    print(json.dumps(result, indent=2))
