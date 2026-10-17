"""Load synthetic trade data from the data/ directory."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

from concord.config import DATA_DIR


def load_trades() -> list[dict]:
    with open(DATA_DIR / "trades.csv", newline="") as f:
        return list(csv.DictReader(f))


def load_trade(trade_id: str) -> dict:
    for row in load_trades():
        if row["trade_id"] == trade_id:
            return row
    raise KeyError(f"Trade {trade_id} not found")


def load_our_confirmation(trade_id: str) -> str:
    path = DATA_DIR / "our_confirmations" / f"{trade_id}.txt"
    return path.read_text()


def load_cpty_confirmation(trade_id: str, version: str) -> Optional[str]:
    """Load counterparty confirmation. In v1, raises on missing file. In v2, returns None."""
    path = DATA_DIR / "cpty_confirmations" / f"{trade_id}.txt"
    if not path.exists():
        if version == "v1":
            raise FileNotFoundError(f"No counterparty confirmation for {trade_id}")
        return None
    return path.read_text()


def load_custodian_status(trade_id: str) -> dict:
    with open(DATA_DIR / "custodian_status.csv", newline="") as f:
        for row in csv.DictReader(f):
            if row["trade_id"] == trade_id:
                return row
    raise KeyError(f"Custodian status for {trade_id} not found")


def load_ssi_registry(version: str) -> dict:
    """v1 reads the stale snapshot; v2 reads the current registry."""
    if version == "v1":
        path = DATA_DIR / "ssi_snapshot.json"
    else:
        path = DATA_DIR / "ssi_registry.json"
    return json.loads(path.read_text())


def load_bank_directory() -> dict[str, dict]:
    """Returns {bank_code: {institution, branch, country}}."""
    result = {}
    with open(DATA_DIR / "bank_directory.csv", newline="") as f:
        for row in csv.DictReader(f):
            result[row["bank_code"]] = row
    return result


def load_email(trade_id: str) -> Optional[str]:
    path = DATA_DIR / "emails" / f"{trade_id}.txt"
    if path.exists():
        return path.read_text()
    return None


def load_scenarios() -> list[dict]:
    with open(DATA_DIR / "scenarios.csv", newline="") as f:
        return list(csv.DictReader(f))
