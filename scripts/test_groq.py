"""Smoke-test Groq connectivity using .env1 or .env (never prints the API key)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, value = s.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    env1 = _load_env_file(ROOT / ".env1")
    env = _load_env_file(ROOT / ".env")

    api_key = (
        env1.get("GROQ_API_KEY")
        or env1.get("LLM_API_KEY")
        or env.get("GROQ_API_KEY")
        or env.get("LLM_API_KEY")
        or ""
    )
    model = (
        env1.get("LLM_MODEL")
        or env.get("LLM_MODEL")
        or "openai/gpt-oss-20b"
    )
    base_url = (
        env1.get("LLM_BASE_URL")
        or env.get("LLM_BASE_URL")
        or "https://api.groq.com/openai/v1"
    )

    print(f".env1 present: {(ROOT / '.env1').exists()} bytes={(ROOT / '.env1').stat().st_size if (ROOT / '.env1').exists() else 0}")
    print(f"API key loaded: {bool(api_key)} (len={len(api_key)})")
    print(f"Model: {model}")

    if not api_key:
        print("FAIL: No GROQ_API_KEY found in .env1 or .env")
        return 1

    # Ensure project client uses this key even if process env differs.
    os.environ["GROQ_API_KEY"] = api_key
    os.environ["LLM_PROVIDER"] = "groq"
    os.environ["USE_MOCK_LLM"] = "false"
    os.environ["LLM_MODEL"] = model
    os.environ["LLM_BASE_URL"] = base_url

    from src.llm.client import GroqLLMClient

    client = GroqLLMClient(
        api_key=api_key,
        model=model,
        temperature=0.2,
        # Let the groq SDK use its default base URL unless customized.
        base_url=None if "api.groq.com" in base_url else base_url,
    )

    print("Calling Groq...")
    try:
        content = client.complete(
            system_prompt="Reply with exactly one short sentence.",
            user_prompt="Say: Groq connection OK",
        )
    except Exception as exc:  # noqa: BLE001 - smoke test should surface any failure
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return 2

    preview = (content or "").strip().replace("\n", " ")
    if len(preview) > 120:
        preview = preview[:117] + "..."
    print(f"PASS: Groq responded ({len(content or '')} chars): {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
