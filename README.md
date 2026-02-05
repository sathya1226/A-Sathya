# Autonomous Insurance Claims Processing Agent

This repository contains a lightweight FNOL (First Notice of Loss) processing agent that:
- extracts key claim fields from `.txt` and `.pdf` documents,
- identifies missing mandatory fields,
- checks simple inconsistency signals,
- recommends a routing workflow,
- and provides concise reasoning for that decision.

## Output format
The agent produces JSON in the required format:

```json
{
  "extractedFields": {},
  "missingFields": [],
  "recommendedRoute": "",
  "reasoning": ""
}
```

## Routing rules implemented
1. If incident description contains `fraud`, `inconsistent`, or `staged` → `Investigation Flag`
2. If any mandatory field is missing → `Manual review`
3. If claim type is `injury` → `Specialist Queue`
4. If estimated damage `< 25000` → `Fast-track`
5. Otherwise → `Manual review`

Additionally, if inconsistency checks are triggered (e.g., initial estimate far exceeds estimated damage), the claim is forced to `Manual review`.

## Project structure
- `claims_agent.py` — CLI + extraction, validation, and routing engine.
- `samples/` — sample FNOL `.txt` files for demonstration.

## Prerequisites
- Python 3.9+
- Optional for PDF parsing: `pypdf`

Install optional dependency:

```bash
pip install pypdf
```

## Run
Process a sample file:

```bash
python3 claims_agent.py samples/fnol_1.txt --pretty
```

Process a PDF:

```bash
python3 claims_agent.py /path/to/document.pdf --pretty
```

## Example outputs
- `samples/fnol_1.txt` → expected `Fast-track`
- `samples/fnol_2.txt` → expected `Investigation Flag`
- `samples/fnol_3.txt` → expected `Specialist Queue`

## Approach
1. **Document loading**: detect extension and read TXT/PDF.
2. **Field extraction**: regex patterns with multiple label aliases per field.
3. **Validation**: compute missing mandatory fields.
4. **Inconsistency checks**: basic cross-field sanity checks.
5. **Decisioning**: apply deterministic routing rules and generate explanation.

## Notes
- The extractor is intentionally lightweight and heuristic-driven for rapid implementation.
- For production, this can be upgraded with schema-based LLM extraction and confidence scoring.
