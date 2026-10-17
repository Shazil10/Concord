"""LLM calls via Nicrron (OpenAI-compatible). Used for parsing, explaining, and drafting."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from concord.config import CONCORD_MODEL, DEMO_DATE, NICRRON_API_KEY, NICRRON_BASE_URL

_client = OpenAI(base_url=NICRRON_BASE_URL, api_key=NICRRON_API_KEY)

PARSE_SYSTEM = """You parse trade confirmations into structured JSON.
Return ONLY valid JSON with these fields:
- counterparty: string
- trade_id: string
- product: "FX" or "BOND"
- trade_date: YYYY-MM-DD
- settle_date: YYYY-MM-DD (also called value_date)
- side: "BUY" or "SELL" (from the sender's perspective)
- ccy_bought: string or null
- amount_bought: number or null
- ccy_sold: string or null
- amount_sold: number or null
- rate_or_price: number or null
- security_id: string or null
- quantity: number or null
- pay_bank_code: string or null
- pay_bank_name: string or null
- pay_branch: string or null
- pay_country: string or null
- pay_account: string or null
- pay_account_name: string or null
- receive_bank_code: string or null
- receive_bank_name: string or null
- receive_branch: string or null
- receive_country: string or null
- receive_account: string or null
- receive_account_name: string or null

For counterparty confirmations that only show pay instructions (where they want us to send cash),
set those as pay_ fields. Dates may be in various formats; normalize to YYYY-MM-DD.
Amounts may have commas; return plain numbers. If a field is absent, use null."""

EXPLAIN_SYSTEM = """You are a trade settlement operations analyst. Given a trade and its breaks,
write a concise explanation. For each break, state: what field mismatched, our value, their value,
the registry value, and whose fault it is (us, counterparty, or unknown).

Return JSON:
{
  "explanation": "one paragraph summary",
  "fault": "us" | "counterparty" | "custodian" | "unknown",
  "urgency": "call" | "email" | "none",
  "urgency_reason": "string"
}

Rules:
- fault=us when our confirmation has wrong data vs the registry
- fault=counterparty when their confirmation has wrong data vs the registry
- urgency=call when settle_date is today (2026-10-17) and there is a break
- urgency=email when settle_date is 2+ days out and there is a break
- urgency=none when no breaks"""

DRAFT_SYSTEM = """You draft settlement operations messages. Given the trade details, breaks,
fault, and urgency, write a professional but concise message.

Address every message to the counterparty by name.
If fault is "us", say we are amending our confirmation to the registry instruction and ask
them to confirm it. If fault is "counterparty", ask them for an amended confirmation.

For email: name the field, our value, their value, registry value. Ask for an amended
confirmation before value date. Do not threaten or quote penalty schedules.

For call: write short talking points. State the cash amount and the account that is wrong.
Ask them not to release.

End with: "This note was not sent."

For release: write "Matched. Ready to release."

Return JSON: {"message": "the draft text", "recipient": "counterparty name or internal"}"""


def _extract_json(text: str) -> dict:
    """Extract JSON from a response that may have markdown fences."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def _call(system: str, user_content: str, retry: bool = True) -> dict:
    """Make an LLM call and parse the JSON response. Retry once on parse failure."""
    resp = _client.chat.completions.create(
        model=CONCORD_MODEL,
        temperature=0,
        max_tokens=1500,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
    )
    raw = resp.choices[0].message.content or ""
    tokens = {
        "input": resp.usage.prompt_tokens if resp.usage else 0,
        "output": resp.usage.completion_tokens if resp.usage else 0,
    }
    try:
        return {"data": _extract_json(raw), "raw": raw, "tokens": tokens, "model": CONCORD_MODEL}
    except (json.JSONDecodeError, ValueError):
        if retry:
            resp2 = _client.chat.completions.create(
                model=CONCORD_MODEL,
                temperature=0,
                max_tokens=1500,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": "That was not valid JSON. Return ONLY valid JSON, no markdown fences."},
                ],
            )
            raw2 = resp2.choices[0].message.content or ""
            tokens["input"] += resp2.usage.prompt_tokens if resp2.usage else 0
            tokens["output"] += resp2.usage.completion_tokens if resp2.usage else 0
            return {"data": _extract_json(raw2), "raw": raw2, "tokens": tokens, "model": CONCORD_MODEL}
        raise


def parse_confirmation(text: str) -> dict:
    try:
        result = _call(PARSE_SYSTEM, text)
    except (json.JSONDecodeError, ValueError):
        result = {"data": {}, "raw": "", "tokens": {"input": 0, "output": 0}, "model": CONCORD_MODEL}
    parsed = result.get("data") or {}
    # Deterministic fallback: extract structured fields from the raw text
    # when LLM fails to produce them
    parsed = _fill_from_text(parsed, text)
    result["data"] = parsed
    return result


def _fill_from_text(parsed: dict, text: str) -> dict:
    """Fill missing fields from structured confirmation text using regex.
    The confirmation format uses 'Pay to <field>: <value>' and 'Receive at <field>: <value>'."""
    field_map = {
        r"Pay (?:to |cash to )?bank code:\s*(\S+)": "pay_bank_code",
        r"Pay (?:to |cash to )?bank:\s*(.+)": "pay_bank_name",
        r"Pay (?:to |cash to )?branch:\s*(.+)": "pay_branch",
        r"Pay (?:to |cash to )?country:\s*(.+)": "pay_country",
        r"Pay (?:to |cash to )?account:\s*(\S+)": "pay_account",
        r"Pay (?:to |cash to )?account name:\s*(.+)": "pay_account_name",
        r"Receive (?:at |from )?bank code:\s*(\S+)": "receive_bank_code",
        r"Receive (?:at |from )?bank:\s*(.+)": "receive_bank_name",
        r"Receive (?:at |from )?branch:\s*(.+)": "receive_branch",
        r"Receive (?:at |from )?country:\s*(.+)": "receive_country",
        r"Receive (?:at |from )?account:\s*(\S+)": "receive_account",
        r"Receive (?:at |from )?account name:\s*(.+)": "receive_account_name",
    }
    for pattern, key in field_map.items():
        if not parsed.get(key):
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                parsed[key] = m.group(1).strip()

    # Also fill basic trade fields if missing
    basic_map = {
        r"Trade id:\s*(\S+)": "trade_id",
        r"Counterparty:\s*(.+)": "counterparty",
        r"(?:Settle|Value)\s*date:\s*(\S+)": "settle_date",
        r"Trade date:\s*(\S+)": "trade_date",
        r"Rate:\s*(\S+)": "rate_or_price",
        r"Price:\s*(\S+)": "rate_or_price",
    }
    for pattern, key in basic_map.items():
        if not parsed.get(key):
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                parsed[key] = m.group(1).strip()

    # Extract amounts
    for pattern, ccy_key, amt_key in [
        (r"(?:We |You )?buy[:\s]+([A-Z]{3})\s+([\d,]+(?:\.\d+)?)", "ccy_bought", "amount_bought"),
        (r"(?:We |You )?sell[:\s]+([A-Z]{3})\s+([\d,]+(?:\.\d+)?)", "ccy_sold", "amount_sold"),
    ]:
        if not parsed.get(amt_key):
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                parsed[ccy_key] = m.group(1).upper()
                parsed[amt_key] = float(m.group(2).replace(",", ""))

    return parsed


def explain_breaks(trade: dict, breaks: list[dict], email_text: str | None = None,
                   fault: str | None = None) -> dict:
    content = f"Trade: {json.dumps(trade, indent=2)}\n\nBreaks:\n{json.dumps(breaks, indent=2)}"
    if fault:
        content += f"\n\nFault has already been determined by the registry check: {fault}. Explain why."
    if email_text:
        content += f"\n\nCounterparty email:\n{email_text}"
    return _call(EXPLAIN_SYSTEM, content)


def draft_message(trade: dict, breaks: list[dict], fault: str, urgency: str, explanation: str) -> dict:
    content = (
        f"Today is {DEMO_DATE}.\n"
        f"Trade: {json.dumps(trade, indent=2)}\n"
        f"Breaks: {json.dumps(breaks, indent=2)}\n"
        f"Fault: {fault}\nUrgency: {urgency}\n"
        f"Explanation: {explanation}"
    )
    return _call(DRAFT_SYSTEM, content)
