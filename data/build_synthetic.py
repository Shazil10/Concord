"""Write the fictional Concord sample set. Safe to run again.

Nothing in here is taken from an employer system or a procedure document.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BANKS = [
    ("FNBKUSNY", "Fable National", "New York", "United States"),
    ("FNBKKRSE", "Fable National", "Seoul", "Korea"),
    ("WESTGBLN", "Westferry Bank", "London", "United Kingdom"),
    ("QUAYDEFF", "Quay and Company", "Frankfurt", "Germany"),
    ("PINESGSG", "Pine Custody", "Singapore", "Singapore"),
    ("PINEUSCH", "Pine Custody", "Chicago", "United States"),
    ("LARKCHZH", "Lark Clearing", "Zurich", "Switzerland"),
    ("MOORNLAM", "Moor and Holt", "Amsterdam", "Netherlands"),
]

BANK = {code: {"bank_code": code, "bank_name": name, "branch": branch, "country": country} for code, name, branch, country in BANKS}


def acct(code: str, account: str, name: str) -> dict:
    row = dict(BANK[code])
    row["account"] = account
    row["account_name"] = name
    return row


# Current settlement instructions. version 1 is what a stale cache still holds.
# version 2 is a newer instruction whose effective_from is before the demo settle dates.
PARTIES: list[dict] = [
    {
        "party": "Northline Treasury",
        "currency": "USD",
        "purpose": "our_receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("WESTGBLN", "90010001", "Northline Treasury USD")}],
    },
    {
        "party": "Northline Treasury",
        "currency": "EUR",
        "purpose": "our_receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("QUAYDEFF", "90020001", "Northline Treasury EUR")}],
    },
    {
        "party": "Northline Treasury",
        "currency": "GBP",
        "purpose": "our_receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("WESTGBLN", "90030001", "Northline Treasury GBP")}],
    },
    {
        "party": "Northline Treasury",
        "currency": "JPY",
        "purpose": "our_receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("PINESGSG", "90040001", "Northline Treasury JPY")}],
    },
    {
        "party": "Lumen Markets",
        "currency": "USD",
        "purpose": "operating",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("FNBKUSNY", "90011001", "Lumen Markets operating")}],
    },
    {
        "party": "Lumen Markets",
        "currency": "USD",
        "purpose": "collateral",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("FNBKUSNY", "90011099", "Lumen Markets collateral")}],
    },
    {
        "party": "Kite Rowan Securities",
        "currency": "USD",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("WESTGBLN", "90021001", "Kite Rowan USD")}],
    },
    {
        "party": "Kite Rowan Securities",
        "currency": "EUR",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("QUAYDEFF", "90022001", "Kite Rowan EUR")}],
    },
    {
        "party": "Kite Rowan Securities",
        "currency": "GBP",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("WESTGBLN", "90023001", "Kite Rowan GBP")}],
    },
    {
        "party": "Sable Fund Services",
        "currency": "USD",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("LARKCHZH", "90031001", "Sable Fund Services USD")}],
    },
    {
        "party": "Veldt Capital",
        "currency": "USD",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("LARKCHZH", "90041001", "Veldt Capital USD")}],
    },
    {
        "party": "Veldt Capital",
        "currency": "JPY",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("PINESGSG", "90042001", "Veldt Capital JPY")}],
    },
    {
        "party": "Quill Asset Management",
        "currency": "EUR",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("MOORNLAM", "90082001", "Quill Asset Management EUR")}],
    },
    {
        "party": "Marlow Brothers",
        "currency": "USD",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("FNBKUSNY", "90033001", "Marlow Brothers USD")}],
    },
    {
        "party": "Marlow Brothers",
        "currency": "EUR",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("QUAYDEFF", "90034001", "Marlow Brothers EUR")}],
    },
    {
        "party": "Birch Capital",
        "currency": "USD",
        "purpose": "receive",
        "history": [
            {"version": 1, "effective_from": "2024-01-01", **acct("FNBKUSNY", "90051000", "Birch Capital USD")},
            {"version": 2, "effective_from": "2026-09-15", **acct("FNBKUSNY", "90051001", "Birch Capital USD")},
        ],
    },
    {
        "party": "Birch Capital",
        "currency": "EUR",
        "purpose": "receive",
        "history": [
            {"version": 1, "effective_from": "2024-01-01", **acct("QUAYDEFF", "90052000", "Birch Capital EUR")},
            {"version": 2, "effective_from": "2026-10-01", **acct("QUAYDEFF", "90052002", "Birch Capital EUR")},
        ],
    },
    {
        "party": "Holm Securities",
        "currency": "USD",
        "purpose": "receive",
        "history": [
            {"version": 1, "effective_from": "2024-01-01", **acct("WESTGBLN", "90061000", "Holm Securities USD")},
            {"version": 2, "effective_from": "2026-08-01", **acct("WESTGBLN", "90061001", "Holm Securities USD")},
        ],
    },
    {
        "party": "Orion Desk",
        "currency": "USD",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("FNBKUSNY", "90081001", "Orion Desk USD")}],
    },
    {
        "party": "Pebble Street Capital",
        "currency": "USD",
        "purpose": "growth",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("PINESGSG", "90071001", "Pebble Street growth")}],
    },
    {
        "party": "Pebble Street Capital",
        "currency": "USD",
        "purpose": "income",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("PINESGSG", "90071002", "Pebble Street income")}],
    },
    {
        "party": "Cedar Point Markets",
        "currency": "JPY",
        "purpose": "receive",
        "history": [{"version": 1, "effective_from": "2024-01-01", **acct("PINESGSG", "90091001", "Cedar Point JPY")}],
    },
]


def latest(party: str, currency: str, purpose: str | None = None) -> dict:
    matches = [item for item in PARTIES if item["party"] == party and item["currency"] == currency and (purpose is None or item["purpose"] == purpose)]
    if len(matches) != 1:
        raise SystemExit(f"SSI lookup failed for {party} {currency} {purpose}: {len(matches)}")
    return matches[0]["history"][-1]


def version(party: str, currency: str, number: int, purpose: str | None = None) -> dict:
    matches = [item for item in PARTIES if item["party"] == party and item["currency"] == currency and (purpose is None or item["purpose"] == purpose)]
    if len(matches) != 1:
        raise SystemExit(f"SSI version lookup failed for {party} {currency} {purpose}")
    for row in matches[0]["history"]:
        if row["version"] == number:
            return row
    raise SystemExit(f"missing version {number} for {party} {currency}")


OUR = "Northline Treasury"


def our(currency: str) -> dict:
    return latest(OUR, currency, "our_receive")


# pay = where we send cash. receive = where we take cash or securities in.
# For a clean trade, pay is the counterparty's current account and receive is ours.
TRADES: list[dict] = [
    dict(trade_id="T001", product="FX", failure_type="clean", expected_decision="Release", expected_fault="none",
         counterparty="Lumen Markets", side="BUY", trade_date="2026-10-15", settle_date="2026-10-17",
         ccy_bought="EUR", amount_bought="5000000", ccy_sold="USD", amount_sold="5450000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="New York",
         pay=latest("Lumen Markets", "USD", "operating"), receive=our("EUR"),
         custodian="Westferry Investor Services", custodian_status="READY",
         notes="Clean FX spot. Both confirms use the current operating account."),
    dict(trade_id="T002", product="FX", failure_type="clean", expected_decision="Release", expected_fault="none",
         counterparty="Kite Rowan Securities", side="BUY", trade_date="2026-10-10", settle_date="2026-10-21",
         ccy_bought="GBP", amount_bought="2000000", ccy_sold="USD", amount_sold="2540000", rate_or_price="1.2700",
         security_id="", quantity="", settlement_location="London",
         pay=latest("Kite Rowan Securities", "USD"), receive=our("GBP"),
         custodian="Westferry Investor Services", custodian_status="READY",
         notes="Clean FX forward."),
    dict(trade_id="T003", product="BOND", failure_type="clean", expected_decision="Release", expected_fault="none",
         counterparty="Sable Fund Services", side="BUY", trade_date="2026-10-16", settle_date="2026-10-19",
         ccy_bought="", amount_bought="", ccy_sold="USD", amount_sold="9850000", rate_or_price="98.50",
         security_id="NLGV 4.25 15JUN2031", quantity="10000000", settlement_location="New York",
         pay=latest("Sable Fund Services", "USD"), receive=our("USD"),
         custodian="Lark Clearing", custodian_status="READY",
         notes="Clean bond purchase. Cash settlement amount is price times quantity over 100."),
    dict(trade_id="T004", product="FX", failure_type="clean", expected_decision="Release", expected_fault="none",
         counterparty="Veldt Capital", side="BUY", trade_date="2026-10-16", settle_date="2026-10-20",
         ccy_bought="JPY", amount_bought="750000000", ccy_sold="USD", amount_sold="5000000", rate_or_price="150.00",
         security_id="", quantity="", settlement_location="Singapore",
         pay=latest("Veldt Capital", "USD"), receive=our("JPY"),
         custodian="Pine Custody Services", custodian_status="READY",
         notes="Clean FX spot."),
    dict(trade_id="T005", product="BOND", failure_type="clean", expected_decision="Release", expected_fault="none",
         counterparty="Quill Asset Management", side="SELL", trade_date="2026-10-14", settle_date="2026-10-21",
         ccy_bought="EUR", amount_bought="4050000", ccy_sold="", amount_sold="", rate_or_price="101.25",
         security_id="HBND 3.10 01MAR2029", quantity="4000000", settlement_location="Frankfurt",
         pay=our("EUR"), receive=our("EUR"),
         custodian="Moor and Holt", custodian_status="READY",
         notes="Clean bond sale. Cash is paid to our EUR account. Their confirm names that same account."),
    dict(trade_id="T006", product="FX", failure_type="clean", expected_decision="Release", expected_fault="none",
         counterparty="Marlow Brothers", side="BUY", trade_date="2026-10-16", settle_date="2026-10-19",
         ccy_bought="USD", amount_bought="3000120", ccy_sold="EUR", amount_sold="2760000", rate_or_price="1.0870",
         security_id="", quantity="", settlement_location="Frankfurt",
         pay=latest("Marlow Brothers", "EUR"), receive=our("USD"),
         custodian="Quay and Company", custodian_status="READY",
         notes="Clean FX spot. We pay EUR."),
    dict(trade_id="T007", product="FX", failure_type="stale_ssi", expected_decision="Hold", expected_fault="us",
         counterparty="Birch Capital", side="BUY", trade_date="2026-10-15", settle_date="2026-10-19",
         ccy_bought="EUR", amount_bought="1200000", ccy_sold="USD", amount_sold="1308000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="New York",
         pay=version("Birch Capital", "USD", 1), receive=our("EUR"),
         current_pay=version("Birch Capital", "USD", 2),
         custodian="Westferry Investor Services", custodian_status="INSTRUCTION_HELD",
         email=True, notes="Stale USD account 90051000 on both confirms. Registry version 2 is 90051001 from 2026-09-15. Email asks us to update. v1 snapshot still has version 1, so v1 can wrongly Release."),
    dict(trade_id="T008", product="FX", failure_type="stale_ssi", expected_decision="Hold", expected_fault="us",
         counterparty="Birch Capital", side="BUY", trade_date="2026-10-16", settle_date="2026-10-17",
         ccy_bought="GBP", amount_bought="800000", ccy_sold="EUR", amount_sold="940000", rate_or_price="1.1750",
         security_id="", quantity="", settlement_location="Frankfurt",
         pay=version("Birch Capital", "EUR", 1), receive=our("GBP"),
         current_pay=version("Birch Capital", "EUR", 2),
         custodian="Quay and Company", custodian_status="INSTRUCTION_HELD",
         email=True, notes="Settles today. Stale EUR account 90052000. Registry version 2 is 90052002 from 2026-10-01. Urgency: call, do not wait on email. Scorecard decision stays Hold."),
    dict(trade_id="T009", product="BOND", failure_type="stale_ssi", expected_decision="Hold", expected_fault="us",
         counterparty="Holm Securities", side="BUY", trade_date="2026-10-14", settle_date="2026-10-21",
         ccy_bought="", amount_bought="", ccy_sold="USD", amount_sold="5940000", rate_or_price="99.00",
         security_id="SLBV 2.80 01DEC2028", quantity="6000000", settlement_location="London",
         pay=version("Holm Securities", "USD", 1), receive=our("USD"),
         current_pay=version("Holm Securities", "USD", 2),
         custodian="Westferry Investor Services", custodian_status="INSTRUCTION_HELD",
         email=True, notes="Bond. Stale USD account 90061000. Registry version 2 is 90061001 from 2026-08-01."),
    dict(trade_id="T010", product="FX", failure_type="stale_ssi", expected_decision="Hold", expected_fault="us",
         counterparty="Holm Securities", side="BUY", trade_date="2026-10-16", settle_date="2026-10-20",
         ccy_bought="EUR", amount_bought="2500000", ccy_sold="USD", amount_sold="2725000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="London",
         pay=version("Holm Securities", "USD", 1), receive=our("EUR"),
         current_pay=version("Holm Securities", "USD", 2),
         custodian="Westferry Investor Services", custodian_status="INSTRUCTION_HELD",
         email=True, notes="Stale USD account 90061000. Same Holm change as T009. Email is enough; value date is 2026-10-20."),
    dict(trade_id="T011", product="FX", failure_type="wrong_branch", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Orion Desk", side="BUY", trade_date="2026-10-15", settle_date="2026-10-19",
         ccy_bought="EUR", amount_bought="900000", ccy_sold="USD", amount_sold="981000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="New York",
         pay=latest("Orion Desk", "USD"), receive=our("EUR"),
         cpty_pay=acct("FNBKKRSE", "90081001", "Orion Desk USD"),
         messy=True,
         custodian="Fable National New York", custodian_status="INSTRUCTION_HELD",
         notes="Same institution, wrong branch. Registry and our confirm: Fable National New York FNBKUSNY. Their confirm: Fable National Seoul FNBKKRSE. Account number matches."),
    dict(trade_id="T012", product="BOND", failure_type="wrong_branch", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Pebble Street Capital", side="BUY", trade_date="2026-10-16", settle_date="2026-10-17",
         ccy_bought="", amount_bought="", ccy_sold="USD", amount_sold="2500000", rate_or_price="100.00",
         security_id="PBBL 5.00 15JAN2030", quantity="2500000", settlement_location="Singapore",
         pay=latest("Pebble Street Capital", "USD", "growth"), receive=our("USD"),
         cpty_pay=acct("PINEUSCH", "90071001", "Pebble Street growth"),
         messy=True,
         custodian="Pine Custody Services", custodian_status="INSTRUCTION_HELD",
         notes="Settles today. Growth account 90071001 is right, but their confirm names Pine Custody Chicago instead of Singapore. Urgency: call. Scorecard decision stays Hold."),
    dict(trade_id="T013", product="FX", failure_type="wrong_branch", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Cedar Point Markets", side="BUY", trade_date="2026-10-16", settle_date="2026-10-22",
         ccy_bought="JPY", amount_bought="300000000", ccy_sold="USD", amount_sold="2000000", rate_or_price="150.00",
         security_id="", quantity="", settlement_location="Singapore",
         pay=latest("Cedar Point Markets", "JPY"), receive=our("JPY"),
         cpty_pay=acct("PINEUSCH", "90091001", "Cedar Point JPY"),
         custodian="Pine Custody Services", custodian_status="INSTRUCTION_HELD",
         notes="Their confirm sends our USD to Pine Custody Chicago."),
]

# T013 correction is applied below after the list is reviewed in code.
# We buy JPY / sell USD, so cash we pay is USD. Cedar only has a JPY SSI in the registry.
# Give Cedar a USD receive account and point the wrong branch at that USD payment.
CEDAR_USD = acct("PINESGSG", "90091002", "Cedar Point USD")
PARTIES.append({
    "party": "Cedar Point Markets",
    "currency": "USD",
    "purpose": "receive",
    "history": [{"version": 1, "effective_from": "2024-01-01", **CEDAR_USD}],
})
TRADES[12]["pay"] = latest("Cedar Point Markets", "USD")
TRADES[12]["receive"] = our("JPY")
TRADES[12]["cpty_pay"] = acct("PINEUSCH", "90091002", "Cedar Point USD")
TRADES[12]["notes"] = "Their confirm sends our USD to Pine Custody Chicago. Registry says Pine Custody Singapore, same account number 90091002."

TRADES.extend([
    dict(trade_id="T014", product="FX", failure_type="shared_code_wrong_account", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Pebble Street Capital", side="BUY", trade_date="2026-10-15", settle_date="2026-10-19",
         ccy_bought="EUR", amount_bought="700000", ccy_sold="USD", amount_sold="763000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="Singapore",
         pay=latest("Pebble Street Capital", "USD", "growth"), receive=our("EUR"),
         cpty_pay=latest("Pebble Street Capital", "USD", "income"),
         messy=True,
         custodian="Pine Custody Services", custodian_status="INSTRUCTION_HELD",
         notes="Same bank code PINESGSG. This trade belongs to the growth account 90071001. Their confirm uses the income account 90071002."),
    dict(trade_id="T015", product="BOND", failure_type="shared_code_wrong_account", expected_decision="Hold", expected_fault="us",
         counterparty="Pebble Street Capital", side="BUY", trade_date="2026-10-14", settle_date="2026-10-21",
         ccy_bought="", amount_bought="", ccy_sold="USD", amount_sold="7780000", rate_or_price="97.25",
         security_id="PBBL 4.00 01NOV2030", quantity="8000000", settlement_location="Singapore",
         pay=latest("Pebble Street Capital", "USD", "income"), receive=our("USD"),
         cpty_pay=latest("Pebble Street Capital", "USD", "growth"),
         custodian="Pine Custody Services", custodian_status="INSTRUCTION_HELD",
         notes="Our confirm pays the income account 90071002. Their confirm and the growth purpose on the trade say 90071001. Fault is us. Bank code PINESGSG matches either way."),
    dict(trade_id="T016", product="FX", failure_type="shared_code_wrong_account", expected_decision="Hold", expected_fault="us",
         counterparty="Lumen Markets", side="BUY", trade_date="2026-10-16", settle_date="2026-10-20",
         ccy_bought="EUR", amount_bought="1500000", ccy_sold="USD", amount_sold="1635000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="New York",
         pay=latest("Lumen Markets", "USD", "collateral"), receive=our("EUR"),
         cpty_pay=latest("Lumen Markets", "USD", "operating"),
         custodian="Fable National New York", custodian_status="INSTRUCTION_HELD",
         notes="Our confirm uses Lumen's collateral account 90011099. Their confirm uses the operating account 90011001. Same bank code FNBKUSNY. Fault is us."),
    dict(trade_id="T017", product="FX", failure_type="swapped_sides", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Kite Rowan Securities", side="BUY", trade_date="2026-10-15", settle_date="2026-10-19",
         ccy_bought="EUR", amount_bought="1000000", ccy_sold="USD", amount_sold="1090000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="London",
         pay=latest("Kite Rowan Securities", "USD"), receive=our("EUR"),
         swapped=True,
         custodian="Westferry Investor Services", custodian_status="INSTRUCTION_HELD",
         notes="We pay USD and receive EUR. Their confirm copies our direction: they also say they pay USD and receive EUR. Our pay must match their receive."),
    dict(trade_id="T018", product="BOND", failure_type="swapped_sides", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Sable Fund Services", side="BUY", trade_date="2026-10-15", settle_date="2026-10-21",
         ccy_bought="", amount_bought="", ccy_sold="USD", amount_sold="3060000", rate_or_price="102.00",
         security_id="SBLB 4.00 01NOV2030", quantity="3000000", settlement_location="Zurich",
         pay=latest("Sable Fund Services", "USD"), receive=our("USD"),
         swapped=True,
         custodian="Lark Clearing", custodian_status="INSTRUCTION_HELD",
         notes="We buy the bond and pay USD. Their confirm says they pay the cash and we deliver the bond."),
    dict(trade_id="T019", product="FX", failure_type="missing_cpty_confirm", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Quill Asset Management", side="BUY", trade_date="2026-10-16", settle_date="2026-10-17",
         ccy_bought="USD", amount_bought="1635000", ccy_sold="EUR", amount_sold="1500000", rate_or_price="1.0900",
         security_id="", quantity="", settlement_location="Amsterdam",
         pay=latest("Quill Asset Management", "EUR"), receive=our("USD"),
         missing_cpty=True,
         custodian="Moor and Holt", custodian_status="AWAITING_CONFIRMATION",
         notes="No counterparty confirmation file. Settles today. v1 should crash with no decision. v2 should Hold and chase. Urgency: call."),
    dict(trade_id="T020", product="BOND", failure_type="missing_cpty_confirm", expected_decision="Hold", expected_fault="counterparty",
         counterparty="Veldt Capital", side="BUY", trade_date="2026-10-16", settle_date="2026-10-23",
         ccy_bought="", amount_bought="", ccy_sold="USD", amount_sold="5025000", rate_or_price="100.50",
         security_id="VLDB 3.50 01SEP2032", quantity="5000000", settlement_location="Zurich",
         pay=latest("Veldt Capital", "USD"), receive=our("USD"),
         missing_cpty=True,
         custodian="Lark Clearing", custodian_status="AWAITING_CONFIRMATION",
         notes="No counterparty confirmation file. Value date is 2026-10-23, so an email chase is enough. v1 crashes. v2 Holds."),
])


# What a custodian knows before our instruction arrives: the cash it expects and its cutoff.
# It does not know whether either confirmation is right.
CUTOFFS = {
    "Westferry Investor Services": "Cash cutoff 15:00 London",
    "Lark Clearing": "Cash cutoff 14:00 Zurich",
    "Pine Custody Services": "Cash cutoff 16:00 Singapore",
    "Moor and Holt": "Cash cutoff 15:30 Amsterdam",
    "Quay and Company": "Cash cutoff 15:00 Frankfurt",
    "Fable National New York": "Cash cutoff 17:00 New York",
}


def money(currency: str, amount: str) -> str:
    if not currency or not amount:
        return ""
    return f"{currency} {int(amount):,}"


def ssi_block(label: str, row: dict) -> list[str]:
    return [
        f"{label} bank code: {row['bank_code']}",
        f"{label} bank: {row['bank_name']}",
        f"{label} branch: {row['branch']}",
        f"{label} country: {row['country']}",
        f"{label} account: {row['account']}",
        f"{label} account name: {row['account_name']}",
    ]


def our_text(trade: dict) -> str:
    pay = trade["pay"]
    receive = trade["receive"]
    lines = [
        "OUR CONFIRMATION",
        "Sender: Northline Treasury",
        f"Trade id: {trade['trade_id']}",
        f"Product: {trade['product']}",
        f"Counterparty: {trade['counterparty']}",
        f"Trade date: {trade['trade_date']}",
        f"Settle date: {trade['settle_date']}",
        f"Our side: {trade['side']}",
    ]
    if trade["product"] == "BOND":
        lines += [
            f"Security: {trade['security_id']}",
            f"Quantity: {int(trade['quantity']):,}",
            f"Price: {trade['rate_or_price']}",
        ]
    else:
        lines += [
            f"We buy: {money(trade['ccy_bought'], trade['amount_bought'])}",
            f"We sell: {money(trade['ccy_sold'], trade['amount_sold'])}",
            f"Rate: {trade['rate_or_price']}",
        ]
    if trade["side"] == "SELL":
        lines += ["", "Cash is payable to us"]
        lines += ssi_block("Receive at", receive)
    else:
        lines += ["", "Our payment instruction"]
        lines += ssi_block("Pay to", pay)
        lines += ["", "Our receive instruction"]
        lines += ssi_block("Receive at", receive)
    lines += ["", "Nothing in this message has been sent to a network."]
    return "\n".join(lines) + "\n"


def cpty_text(trade: dict) -> str:
    pay = trade.get("cpty_pay", trade["pay"])
    receive = trade["receive"]
    if trade.get("swapped"):
        # They repeat our direction instead of the mirror image.
        lines = [
            "COUNTERPARTY CONFIRMATION",
            f"From: {trade['counterparty']}",
            f"Re: {trade['trade_id']}",
            f"Trade date {trade['trade_date']} value {trade['settle_date']}",
            "We confirm the following:",
        ]
        if trade["product"] == "FX":
            lines.append(f"We buy {money(trade['ccy_bought'], trade['amount_bought'])}.")
            lines.append(f"We sell {money(trade['ccy_sold'], trade['amount_sold'])} at {trade['rate_or_price']}.")
        else:
            lines.append(f"We buy {trade['security_id']}, quantity {int(trade['quantity']):,}, price {trade['rate_or_price']}.")
            lines.append(f"We pay cash {money(trade['ccy_sold'], trade['amount_sold'])}.")
        lines += ssi_block("Pay to", receive)
        lines += ssi_block("Receive at", pay)
        return "\n".join(lines) + "\n"

    if trade.get("messy"):
        settle = trade["settle_date"]
        year, month, day = settle.split("-")
        shown = f"{day}/{month}/{year}"
        lines = [
            f"note from {trade['counterparty']} ops — please ignore the footer, the fax header was wrong",
            f"value date {shown}",
            f"ref {trade['trade_id']}",
            f"acct no. {pay['account']}",
            f"bank {pay['bank_name']} / {pay['branch']} / code {pay['bank_code']}",
            f"country {pay['country']}",
        ]
        if trade["product"] == "FX":
            lines.insert(3, f"we see you buying {trade['ccy_bought']} {int(trade['amount_bought']):,} against {trade['ccy_sold']} {int(trade['amount_sold']):,} at {trade['rate_or_price']}")
        else:
            lines.insert(3, f"bond {trade['security_id']} nominal {int(trade['quantity']):,} price {trade['rate_or_price']} cash {trade['ccy_sold']} {int(trade['amount_sold']):,}")
        lines.append(f"your trade date was {trade['trade_date'][8:]}.{trade['trade_date'][5:7]}.{trade['trade_date'][0:4]}")
        lines.append("kind regards, settlements")
        return "\n".join(lines) + "\n"

    lines = [
        "COUNTERPARTY CONFIRMATION",
        f"From: {trade['counterparty']}",
        f"Trade id: {trade['trade_id']}",
        f"Trade date: {trade['trade_date']}",
        f"Value date: {trade['settle_date']}",
        "We receive the cash you pay. You receive the other side.",
    ]
    if trade["product"] == "FX":
        lines.append(f"You buy {money(trade['ccy_bought'], trade['amount_bought'])}.")
        lines.append(f"You sell {money(trade['ccy_sold'], trade['amount_sold'])} at {trade['rate_or_price']}.")
    else:
        lines.append(f"Security {trade['security_id']}, quantity {int(trade['quantity']):,}, price {trade['rate_or_price']}.")
        lines.append(f"Cash {money(trade['ccy_sold'] or trade['ccy_bought'], trade['amount_sold'] or trade['amount_bought'])}.")
    lines += ssi_block("Pay cash to", pay)
    return "\n".join(lines) + "\n"


def email_text(trade: dict) -> str:
    current = trade["current_pay"]
    old = trade["pay"]
    return "\n".join([
        f"From: settlements@{trade['counterparty'].split()[0].lower()}.example",
        "To: settlements@northline.example",
        f"Subject: New account for {trade['counterparty']}",
        "",
        f"Hello Northline Treasury,",
        "",
        f"Please note our new account, effective {current['effective_from']}.",
        f"Old account {old['account']} at {old['bank_name']} {old['branch']} ({old['bank_code']}) is closed for new settlements.",
        f"New account {current['account']} at {current['bank_name']} {current['branch']} ({current['bank_code']}).",
        f"This applies to {trade['trade_id']} and any open trade settling after the effective date.",
        "",
        "This mailbox is fictional. Do not reply.",
        "",
    ])


# Front office books which account a trade settles to when the counterparty
# has several accounts under one bank code.
SETTLEMENT_PURPOSE = {
    "T001": "operating",
    "T012": "growth",
    "T014": "growth",
    "T015": "growth",
    "T016": "operating",
}


def cash_amount(trade: dict) -> tuple[str, str]:
    if trade["side"] == "SELL" and trade["ccy_bought"]:
        return trade["ccy_bought"], trade["amount_bought"]
    return trade["ccy_sold"], trade["amount_sold"]


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def registry_payload(snapshot: bool) -> dict:
    parties = []
    for item in PARTIES:
        history = [row for row in item["history"] if row["version"] == 1] if snapshot else item["history"]
        parties.append({
            "party": item["party"],
            "currency": item["currency"],
            "purpose": item["purpose"],
            "history": history,
        })
    return {
        "as_of": "2026-08-01" if snapshot else "2026-10-17",
        "description": "Fictional standing settlement instructions.",
        "parties": parties,
    }


def main() -> None:
    if len(TRADES) != 20:
        raise SystemExit(f"expected 20 trades, got {len(TRADES)}")
    ids = [trade["trade_id"] for trade in TRADES]
    if ids != [f"T{n:03d}" for n in range(1, 21)]:
        raise SystemExit(f"trade ids are not T001-T020: {ids}")

    (ROOT / "our_confirmations").mkdir(exist_ok=True)
    (ROOT / "cpty_confirmations").mkdir(exist_ok=True)
    (ROOT / "emails").mkdir(exist_ok=True)
    for folder in ("cpty_confirmations", "emails"):
        for old in (ROOT / folder).glob("*.txt"):
            old.unlink()

    trade_fields = [
        "trade_id", "product", "trade_date", "settle_date", "our_entity", "counterparty", "side",
        "ccy_bought", "amount_bought", "ccy_sold", "amount_sold", "rate_or_price", "security_id",
        "quantity", "settlement_location", "settlement_purpose",
    ]
    trade_rows = []
    scenario_rows = []
    custodian_rows = []
    queue = []
    for trade in TRADES:
        trade_rows.append({"our_entity": OUR, "settlement_purpose": SETTLEMENT_PURPOSE.get(trade["trade_id"], ""), **trade})
        scenario_rows.append({
            "trade_id": trade["trade_id"],
            "product": trade["product"],
            "failure_type": trade["failure_type"],
            "expected_decision": trade["expected_decision"],
            "expected_fault": trade["expected_fault"],
            "notes": trade["notes"],
        })
        currency, amount = cash_amount(trade)
        custodian_rows.append({
            "trade_id": trade["trade_id"],
            "custodian": trade["custodian"],
            "status": "AWAITING_INSTRUCTION",
            "expected_amount": amount,
            "expected_ccy": currency,
            "value_date": trade["settle_date"],
            "notes": CUTOFFS[trade["custodian"]],
        })
        (ROOT / "our_confirmations" / f"{trade['trade_id']}.txt").write_text(our_text(trade))
        if not trade.get("missing_cpty"):
            (ROOT / "cpty_confirmations" / f"{trade['trade_id']}.txt").write_text(cpty_text(trade))
        if trade.get("email"):
            (ROOT / "emails" / f"{trade['trade_id']}.txt").write_text(email_text(trade))
        queue.append({
            "trade_id": trade["trade_id"],
            "product": trade["product"],
            "counterparty": trade["counterparty"],
            "settle_date": trade["settle_date"],
            "decision": trade["expected_decision"],
            "fault": trade["expected_fault"],
            "failure_type": trade["failure_type"],
            "summary": trade["notes"],
        })

    write_csv(ROOT / "trades.csv", trade_rows, trade_fields)
    write_csv(ROOT / "scenarios.csv", scenario_rows, ["trade_id", "product", "failure_type", "expected_decision", "expected_fault", "notes"])
    write_csv(ROOT / "custodian_status.csv", custodian_rows, ["trade_id", "custodian", "status", "expected_amount", "expected_ccy", "value_date", "notes"])
    write_csv(ROOT / "bank_directory.csv", [dict(zip(["bank_code", "institution", "branch", "country"], row)) for row in BANKS], ["bank_code", "institution", "branch", "country"])
    (ROOT / "ssi_registry.json").write_text(json.dumps(registry_payload(False), indent=2) + "\n")
    (ROOT / "ssi_snapshot.json").write_text(json.dumps(registry_payload(True), indent=2) + "\n")
    ui = ROOT.parent / "ui"
    ui.mkdir(exist_ok=True)
    (ui / "sample_queue.json").write_text(json.dumps({"as_of": "2026-10-17", "desk": "Northline Treasury", "trades": queue}, indent=2) + "\n")

    forbidden = ("world bank", "ibrd", "ida ", "miga", "bloomberg", "summit", "murex")
    blob = "\n".join(path.read_text().lower() for path in ROOT.rglob("*") if path.suffix in {".csv", ".json", ".txt"})
    for word in forbidden:
        if word in blob:
            raise SystemExit(f"forbidden token found in sample data: {word}")
    print(f"wrote {len(TRADES)} trades")


if __name__ == "__main__":
    main()
