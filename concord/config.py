"""Load environment and expose configuration constants."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV)

NICRRON_API_KEY = os.environ["NICRRON_API_KEY"]
NICRRON_BASE_URL = "https://api.nicrron.ai/v1"
CONCORD_MODEL = os.getenv("CONCORD_MODEL", "anthropic/claude-fable-5-1")

PRISMTRACE_API_KEY = os.environ["PRISMTRACE_API_KEY"]
PRISMTRACE_PROJECT_ID = os.environ["PRISMTRACE_PROJECT_ID"]
PRISMTRACE_HOST = os.getenv("PRISMTRACE_HOST", "https://api.prism.blockconvey.com")

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS_DIR.mkdir(exist_ok=True)

DEMO_DATE = "2026-10-17"
