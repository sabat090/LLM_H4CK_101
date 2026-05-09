"""PromptLabs — Flag validation utility.

Flags are stored as SHA-256 hashes so reading the source doesn't spoil the answers.
"""
from __future__ import annotations

import hashlib
import re

# Master flag registry: lab_id → SHA-256 hash of expected flag
_FLAG_HASHES: dict[str, str] = {
    "01":   "e069ff1efcc895a54e443fda70561e55a59a02d462618bb4c886be09a71c153f",
    "01-H": "d329a3fe2bb752816c76183f2149c20dbb23966656fa268a4216dd7f6433b413",
    "02a":  "8fc68f0b7aac15e24ad9c7af819217723a5dcf1e4c11e2c848c039f81e490374",
    "02b":  "5447321024c6548be8c365ec84d0577e522a82b99a9bb2de06ba0c4857bad327",
    "03":   "f8ffc89718995e379296c4268d6bfb922a63c6679624cff4c9ce13a6a862d6e7",
    "04":   "28f2803b98e9442688570c6b05f0fd92df83e56345cf5f8cf0bf465cc45b90c0",
}


def check_flag(lab_id: str, submitted: str) -> tuple[bool, str]:
    """Validate a submitted flag. Returns (success, message)."""
    expected_hash = _FLAG_HASHES.get(lab_id)
    if expected_hash is None:
        return False, f"Unknown lab ID: {lab_id}"

    submitted = submitted.strip()
    if not re.match(r"^FLAG\{[^}]+\}$", submitted):
        return False, "Invalid flag format. Expected FLAG{...}"

    submitted_hash = hashlib.sha256(submitted.encode()).hexdigest()
    if submitted_hash == expected_hash:
        return True, f"Correct! Lab {lab_id} solved."
    return False, "Incorrect flag. Keep trying!"
