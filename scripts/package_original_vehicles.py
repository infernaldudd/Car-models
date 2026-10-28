#!/usr/bin/env python3
"""Fail-closed release packager: only explicitly approved original vehicles.

Run from any directory:
  python scripts/package_original_vehicles.py --check
  python scripts/package_original_vehicles.py --package

This is a technical packaging gate, not a legal opinion or replacement for
human review. Unreal's actual build must separately use this approved output.
"""
import argparse
import hashlib
import json
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSET_ROOT = (ROOT / "original_vehicles").resolve()
MANIFEST = ASSET_ROOT / "manifest.json"
REQUIRED_RECORDS = ("authorship_record", "license_or_assignment_record",
                    "legal_approval_record", "name_clearance_record", "quality_report")

def inside_original_vehicles(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Missing or invalid path")
    p = (ROOT / value).resolve()
    if not p.is_relative_to(ASSET_ROOT):
        raise ValueError(f"Release source must be under original_vehicles/: {value!r}")
    return p

def validate():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    approved = []
    known_ids = set()
    for item in data["items"]:
        name = item["id"]
        if name in known_ids:
            raise ValueError(f"Duplicate model id: {name}")
        known_ids.add(name)
        status = item["status"]
        if status not in ("concept_only", "in_development",
                          "qa_pending", "legal_pending", "approved_for_release"):
            raise ValueError(f"Unexpected status: {status}")
        if status != "approved_for_release":
            continue
        if item.get("legal_review") != "approved" or item.get("quality_review") != "approved":
            raise ValueError(f"{name} approved for release without legal and quality approvals")
        if not item.get("owner_signoff"):
            raise ValueError(f"{name} missing owner signoff")
        for field in REQUIRED_RECORDS:
            record = inside_original_vehicles(item.get(field))
            if not record.is_file():
                raise ValueError(f"{name} missing evidence {field}: {record}")
        model = inside_original_vehicles(item.get("glb"))
        if not model.is_file() or model.suffix.lower() != ".glb":
            raise ValueError(f"{name} missing GLB")
        expected = item.get("sha256", "")
        if len(expected) != 64 or not all(c in "0123456789abcdef" for c in expected.lower()):
            raise ValueError(f"{name} missing SHA256 digest")
        actual = hashlib.file_digest(model.open("rb"), "sha256").hexdigest()
        if actual.lower() != expected.lower():
            raise ValueError(f"{name} GLB SHA256 mismatch")
        approved.append((name, model))
    if data["release_approved_count"] != len(approved):
        raise ValueError("release_approved_count does not match manifest approvals")
    return approved

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate manifest without packaging")
    parser.add_argument("--package", action="store_true", help="Create ZIP of approved original GLBs")
    args = parser.parse_args()
    if args.check == args.package:
        parser.error("Choose exactly one of --check or --package")
    approved = validate()
    print(f"Original vehicles approved: {len(approved)}")
    if not args.package:
        return
    if not approved:
        raise ValueError("No original vehicles approved: refusing empty release")
    output = ROOT / "original_vehicles" / "helvetia_approved_original_cars.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for _, model in approved:
            z.write(model, model.relative_to(ROOT))
        z.write(MANIFEST, MANIFEST.relative_to(ROOT))
    print(f"Created {output}")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"RELEASE BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
