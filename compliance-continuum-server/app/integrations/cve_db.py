import requests
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.cve import CVE

NVD_FEED_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=1000&pubStartDate=2024-01-01T00:00:00.000"

# Fetch and update CVEs from NVD
def update_cves(db: Session):
    resp = requests.get(NVD_FEED_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    for item in data.get("vulnerabilities", []):
        cve_id = item["cve"]["id"]
        desc = item["cve"]["descriptions"][0]["value"]
        published = datetime.fromisoformat(item["cve"]["published"][:-1])
        modified = datetime.fromisoformat(item["cve"]["lastModified"][:-1])
        refs = item["cve"].get("references", [])
        cvss = item["cve"].get("metrics", {})
        raw = item
        exists = db.query(CVE).filter(CVE.id == cve_id).first()
        if exists:
            exists.description = desc
            exists.published = published
            exists.last_modified = modified
            exists.references = refs
            exists.cvss = cvss
            exists.raw = raw
        else:
            db.add(CVE(
                id=cve_id,
                description=desc,
                published=published,
                last_modified=modified,
                references=refs,
                cvss=cvss,
                raw=raw
            ))
    db.commit()
