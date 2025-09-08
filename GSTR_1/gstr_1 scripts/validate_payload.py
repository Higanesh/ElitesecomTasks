import os

# ✅ Required files for each marketplace
REQUIRED_FILES = {
    "myntra": ["packed", "rt", "rto"],
    "ajio": ["DropShipGstReports", "DropShipRtvReports"],          # Example: Ajio files
    "limeroad": ["limeroad_report"],    # Example: Limeroad files
}

# ---------- Generic Payload Validation ----------
def validate_payload(payload):
    """
    Validate payload for a specific marketplace.
    payload = {
        "marketplace_name": "myntra",
        "files": ["path/to/file1.csv", "path/to/file2.csv"],
        "user_email": "user@example.com"
    }
    """
    marketplace = payload.get("marketplace_name", "").lower()
    files = payload.get("files", [])
    user_email = payload.get("user_email", "unknown")

    # 1. Check if the marketplace is supported
    required_files = REQUIRED_FILES.get(marketplace)
    if not required_files:
        return False, f"❌ Unsupported marketplace selected by {user_email}: {marketplace}"

    # 2. Check file count
    if len(files) < len(required_files):
        return False, f"❌ Missing files for {marketplace.title()}. Expected {len(required_files)}, got {len(files)}."

    # 3. Check that files exist
    for f in files:
        if not os.path.exists(f):
            return False, f"❌ File not found: {f}"

    # 4. Check that all required files are uploaded
    for req_file in required_files:
        if not any(req_file.lower() in os.path.basename(f).lower() for f in files):
            return False, f"❌ Required file '{req_file}' missing for {marketplace.title()}"

    return True, f"✅ Payload validated successfully for {marketplace.title()} (user: {user_email})"
