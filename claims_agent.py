#!/usr/bin/env python3
"""Autonomous Insurance Claims Processing Agent.

Parses FNOL documents (TXT/PDF), extracts key fields, validates mandatory fields,
and recommends a claim routing decision with short reasoning.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

FIELD_PATTERNS = {
    "policyNumber": [r"policy\s*(?:number|no\.?|#)?\s*[:\-]\s*([A-Z0-9\-]+)"],
    "policyholderName": [
        r"policyholder\s*name\s*[:\-]\s*([^\n]+)",
        r"insured\s*name\s*[:\-]\s*([^\n]+)",
    ],
    "effectiveDates": [
        r"effective\s*dates?\s*[:\-]\s*([^\n]+)",
        r"policy\s*period\s*[:\-]\s*([^\n]+)",
    ],
    "incidentDate": [r"(?:incident|loss)\s*date\s*[:\-]\s*([^\n]+)"],
    "incidentTime": [r"(?:incident|loss)\s*time\s*[:\-]\s*([^\n]+)"],
    "incidentLocation": [r"(?:incident|loss)\s*location\s*[:\-]\s*([^\n]+)"],
    "incidentDescription": [
        r"(?:incident|loss)\s*description\s*[:\-]\s*([\s\S]+?)(?:\n\w[\w\s]*:|$)",
        r"description\s*[:\-]\s*([\s\S]+?)(?:\n\w[\w\s]*:|$)",
    ],
    "claimant": [r"claimant\s*[:\-]\s*([^\n]+)"],
    "thirdParties": [r"third\s*part(?:y|ies)\s*[:\-]\s*([^\n]+)"],
    "contactDetails": [
        r"contact\s*details?\s*[:\-]\s*([^\n]+)",
        r"phone\s*[:\-]\s*([^\n]+)",
        r"email\s*[:\-]\s*([^\n]+)",
    ],
    "assetType": [r"asset\s*type\s*[:\-]\s*([^\n]+)", r"vehicle\s*type\s*[:\-]\s*([^\n]+)"],
    "assetId": [
        r"asset\s*id\s*[:\-]\s*([^\n]+)",
        r"vin\s*[:\-]\s*([^\n]+)",
        r"registration\s*(?:no\.?|number)?\s*[:\-]\s*([^\n]+)",
    ],
    "estimatedDamage": [r"estimated\s*damage\s*[:\-]\s*([^\n]+)"],
    "claimType": [r"claim\s*type\s*[:\-]\s*([^\n]+)"],
    "attachments": [r"attachments?\s*[:\-]\s*([^\n]+)"],
    "initialEstimate": [r"initial\s*estimate\s*[:\-]\s*([^\n]+)"],
}

MANDATORY_FIELDS = [
    "policyNumber",
    "policyholderName",
    "effectiveDates",
    "incidentDate",
    "incidentTime",
    "incidentLocation",
    "incidentDescription",
    "claimant",
    "contactDetails",
    "assetType",
    "assetId",
    "estimatedDamage",
    "claimType",
    "attachments",
    "initialEstimate",
]


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "PDF support requires the optional dependency 'pypdf'. "
                "Install with: pip install pypdf"
            ) from exc

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    raise ValueError(f"Unsupported file type: {path.suffix}")


def normalize(text: str) -> str:
    return re.sub(r"\r\n?", "\n", text)


def extract_field(text: str, patterns: List[str]) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = re.sub(r"\s+", " ", match.group(1)).strip(" .\n\t")
            if value:
                return value
    return None


def parse_currency(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    match = re.search(r"([0-9][0-9,]*(?:\.[0-9]+)?)", value)
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def detect_inconsistencies(fields: Dict[str, str]) -> List[str]:
    issues: List[str] = []

    estimated_damage = parse_currency(fields.get("estimatedDamage"))
    initial_estimate = parse_currency(fields.get("initialEstimate"))
    if estimated_damage is not None and initial_estimate is not None:
        if initial_estimate > estimated_damage * 1.5:
            issues.append("Initial estimate is significantly higher than estimated damage.")

    if fields.get("claimType", "").strip().lower() == "injury":
        asset_type = fields.get("assetType", "").strip().lower()
        if asset_type in {"", "n/a", "none"}:
            issues.append("Injury claim has missing/invalid asset type.")

    return issues


def recommend_route(fields: Dict[str, str], missing_fields: List[str]) -> Tuple[str, str]:
    description = fields.get("incidentDescription", "")
    claim_type = fields.get("claimType", "").strip().lower()
    estimated_damage = parse_currency(fields.get("estimatedDamage"))

    if re.search(r"\b(fraud|inconsistent|staged)\b", description, re.IGNORECASE):
        return "Investigation Flag", "Description contains potential fraud indicators."

    if missing_fields:
        return "Manual review", "One or more mandatory fields are missing."

    if claim_type == "injury":
        return "Specialist Queue", "Claim type is injury and requires specialist handling."

    if estimated_damage is not None and estimated_damage < 25000:
        return "Fast-track", "Estimated damage is below 25,000 threshold."

    return "Manual review", "Claim does not qualify for fast-track based on current rules."


def process_document(path: Path) -> Dict[str, object]:
    text = normalize(read_document(path))

    extracted: Dict[str, str] = {}
    for field, patterns in FIELD_PATTERNS.items():
        value = extract_field(text, patterns)
        if value is not None:
            extracted[field] = value

    missing_fields = [field for field in MANDATORY_FIELDS if field not in extracted]
    inconsistencies = detect_inconsistencies(extracted)

    route, base_reason = recommend_route(extracted, missing_fields)
    if inconsistencies:
        route = "Manual review"

    reasoning_parts = [base_reason]
    if inconsistencies:
        reasoning_parts.append("Inconsistencies detected: " + " ".join(inconsistencies))

    return {
        "extractedFields": extracted,
        "missingFields": missing_fields,
        "recommendedRoute": route,
        "reasoning": " ".join(reasoning_parts),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="FNOL claims processing agent")
    parser.add_argument("document", type=Path, help="Path to FNOL .txt/.pdf document")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    result = process_document(args.document)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
