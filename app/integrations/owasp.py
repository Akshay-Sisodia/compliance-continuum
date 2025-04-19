import subprocess
import json
from pathlib import Path
from typing import List, Dict

# Path to dependency-check CLI and data directory
DEPENDENCY_CHECK_CLI = "dependency-check.sh"  # or dependency-check.bat on Windows
DATA_DIR = "./odc-data"
REPORT_FILE = "./odc-report.json"

# Run OWASP Dependency-Check and parse the JSON report
def run_dependency_check(target_dir: str) -> List[Dict]:
    # Run the CLI tool
    subprocess.run([
        DEPENDENCY_CHECK_CLI,
        "--project", "compliance-continuum-scan",
        "--scan", target_dir,
        "--format", "JSON",
        "--data", DATA_DIR,
        "--out", REPORT_FILE
    ], check=True)
    # Parse the report
    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)
    vulns = []
    for dep in report.get("dependencies", []):
        for vuln in dep.get("vulnerabilities", []):
            vulns.append({
                "dependency": dep.get("fileName"),
                "cve": vuln.get("name"),
                "severity": vuln.get("severity"),
                "description": vuln.get("description"),
                "references": vuln.get("references", []),
            })
    return vulns
