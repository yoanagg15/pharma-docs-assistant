"""Configuration is controlled by the operator, never by model output."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    provider: str = "mock"
    model: str = "qwen/qwen3.8-27b"
    api_url: str = "http://127.0.0.1:8000"
    local_llm_url: str = "http://127.0.0.1:1234/v1"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    runtime: Path = ROOT / "data/runtime"

    def __post_init__(self):
        if self.provider not in {"mock", "groq", "local"}:
            raise ValueError("MODEL_PROVIDER must be mock, groq, or local.")
        for url in (self.api_url, self.local_llm_url):
            parsed = urlparse(url)
            if (
                parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
                or parsed.scheme != "http"
                or parsed.username
                or parsed.password
            ):
                raise ValueError("Demo services must use a configured localhost HTTP address.")

    @classmethod
    def load(cls):
        load_dotenv(ROOT / ".env", override=False)
        # Disable external tracing: this demo does not export conversations to LangSmith.
        os.environ["LANGSMITH_TRACING"] = "false"
        return cls(
            provider=os.getenv("MODEL_PROVIDER", "mock"),
            model=os.getenv("MODEL_NAME", "qwen/qwen3.8-27b"),
            api_url=os.getenv("BUSINESS_API_URL", "http://127.0.0.1:8000").rstrip("/"),
            local_llm_url=os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:1234/v1"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        )
