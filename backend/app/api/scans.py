from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
import asyncio
import re
from urllib.parse import urlparse, urljoin

router = APIRouter()

class ScanCreate(BaseModel):
    url: str

class QuickScanResult(BaseModel):
    url: str
    status: str
    findings: list
    risk_score: int
    endpoints_checked: int
    scan_time_seconds: float

# ── Helper: check a single header ──────────────────────────────────────────
def check_headers(url: str, headers: dict, cookies: list) -> list:
    findings = []
    h = {k.lower(): v for k, v in headers.items()}

    # 1. HSTS
    if "strict-transport-security" not in h:
        findings.append({
            "severity": "high",
            "type": "Missing HSTS",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 6.1,
            "status": "open",
            "desc": "Strict-Transport-Security header not present. Connections can be downgraded to HTTP.",
            "remediation": "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains"
        })

    # 2. CSP
    if "content-security-policy" not in h:
        findings.append({
            "severity": "high",
            "type": "Missing Content-Security-Policy",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 5.8,
            "status": "open",
            "desc": "Content-Security-Policy header is absent. XSS attacks may succeed.",
            "remediation": "Add a strict CSP header, e.g.: Content-Security-Policy: default-src 'self'"
        })

    # 3. X-Frame-Options
    if "x-frame-options" not in h and "content-security-policy" not in h:
        findings.append({
            "severity": "medium",
            "type": "Clickjacking Risk (Missing X-Frame-Options)",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 4.3,
            "status": "open",
            "desc": "X-Frame-Options header missing. Page may be embeddable in iframes (clickjacking).",
            "remediation": "Add: X-Frame-Options: DENY"
        })

    # 4. X-Content-Type-Options
    if "x-content-type-options" not in h:
        findings.append({
            "severity": "low",
            "type": "Missing X-Content-Type-Options",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 3.1,
            "status": "open",
            "desc": "Missing X-Content-Type-Options: nosniff. MIME sniffing attacks possible.",
            "remediation": "Add: X-Content-Type-Options: nosniff"
        })

    # 5. Server version leak
    server = h.get("server", "")
    x_powered = h.get("x-powered-by", "")
    if server and any(c.isdigit() for c in server):
        findings.append({
            "severity": "low",
            "type": "Server Version Disclosure",
            "url": url,
            "param": "-",
            "method": "Header Fingerprint",
            "cvss": 2.6,
            "status": "open",
            "desc": f"Server header reveals version: '{server}'. Aids targeted attacks.",
            "remediation": "Configure server to suppress version info in the Server header."
        })
    if x_powered:
        findings.append({
            "severity": "info",
            "type": "Technology Fingerprint (X-Powered-By)",
            "url": url,
            "param": "-",
            "method": "Header Fingerprint",
            "cvss": 1.5,
            "status": "open",
            "desc": f"X-Powered-By header reveals stack: '{x_powered}'.",
            "remediation": "Remove or mask the X-Powered-By header."
        })

    # 6. Referrer-Policy
    if "referrer-policy" not in h:
        findings.append({
            "severity": "low",
            "type": "Missing Referrer-Policy",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 2.4,
            "status": "open",
            "desc": "Referrer-Policy header not set. Sensitive URLs may leak via Referer header.",
            "remediation": "Add: Referrer-Policy: strict-origin-when-cross-origin"
        })

    # 7. Permissions-Policy
    if "permissions-policy" not in h and "feature-policy" not in h:
        findings.append({
            "severity": "info",
            "type": "Missing Permissions-Policy",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 1.2,
            "status": "open",
            "desc": "Permissions-Policy header not set. Browser features (camera, geolocation) uncontrolled.",
            "remediation": "Add a Permissions-Policy header to restrict browser APIs."
        })

    # 8. Insecure cookies
    for cookie in cookies:
        name = cookie.get("name", "unknown")
        if not cookie.get("httponly", False):
            findings.append({
                "severity": "medium",
                "type": "Cookie Missing HttpOnly Flag",
                "url": url,
                "param": name,
                "method": "Cookie Check",
                "cvss": 4.0,
                "status": "open",
                "desc": f"Cookie '{name}' does not have the HttpOnly flag. Accessible via JavaScript.",
                "remediation": f"Set HttpOnly flag on cookie '{name}'."
            })
        if not cookie.get("secure", False) and url.startswith("https"):
            findings.append({
                "severity": "medium",
                "type": "Cookie Missing Secure Flag",
                "url": url,
                "param": name,
                "method": "Cookie Check",
                "cvss": 3.7,
                "status": "open",
                "desc": f"Cookie '{name}' missing Secure flag. Can be sent over HTTP.",
                "remediation": f"Set Secure flag on cookie '{name}'."
            })

    # 9. Cache-Control for sensitive endpoints
    cache = h.get("cache-control", "")
    if "no-store" not in cache and "private" not in cache:
        findings.append({
            "severity": "info",
            "type": "Potentially Cacheable Response",
            "url": url,
            "param": "-",
            "method": "Header Check",
            "cvss": 1.8,
            "status": "open",
            "desc": "Cache-Control does not include no-store or private. Sensitive data may be cached.",
            "remediation": "Add: Cache-Control: no-store, no-cache, private for authenticated endpoints."
        })

    return findings


def check_open_redirect(url: str, response_url: str) -> list:
    """Detect if a redirect left the original domain."""
    findings = []
    orig = urlparse(url)
    dest = urlparse(str(response_url))
    if dest.netloc and orig.netloc and dest.netloc != orig.netloc:
        findings.append({
            "severity": "medium",
            "type": "Open Redirect",
            "url": url,
            "param": "Location",
            "method": "Redirect Analysis",
            "cvss": 5.1,
            "status": "open",
            "desc": f"Response redirected from {orig.netloc} to external domain {dest.netloc}.",
            "remediation": "Validate redirect URLs against an allowlist of trusted domains."
        })
    return findings


def compute_risk_score(findings: list) -> int:
    if not findings:
        return 0
    weights = {"critical": 10, "high": 7, "medium": 4, "low": 2, "info": 1}
    total = sum(weights.get(f["severity"], 0) for f in findings)
    max_possible = len(findings) * 10
    return min(int((total / max_possible) * 100), 99) if max_possible else 0


# ── Main quick-scan endpoint ────────────────────────────────────────────────
@router.post("/quick")
async def quick_scan(scan_in: ScanCreate):
    import time
    start = time.time()

    raw_url = scan_in.url.strip()
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url

    all_findings = []
    endpoints_checked = 0

    headers_to_send = {
        "User-Agent": "ARES-Scanner/2.4.1 (Security Research)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15.0,
            headers=headers_to_send,
            verify=False  # some targets have self-signed certs
        ) as client:
            # ── Primary request ──────────────────────────────────────────
            resp = await client.get(raw_url)
            endpoints_checked += 1
            final_url = str(resp.url)

            # Open redirect check
            all_findings += check_open_redirect(raw_url, final_url)

            # Header checks on main page
            cookies = [
                {
                    "name": c.name,
                    "httponly": "httponly" in str(c).lower() or c.has_nonstandard_attr("httponly"),
                    "secure": c.secure,
                }
                for c in resp.cookies.jar
            ] if hasattr(resp.cookies, 'jar') else []

            all_findings += check_headers(final_url, dict(resp.headers), cookies)

            # ── Check common sensitive paths ─────────────────────────────
            base = f"{urlparse(final_url).scheme}://{urlparse(final_url).netloc}"
            sensitive_paths = [
                ("/robots.txt", "Robots.txt Exposed"),
                ("/.git/HEAD", "Git Repository Exposed"),
                ("/admin", "Admin Panel"),
                ("/phpinfo.php", "PHPInfo Exposed"),
                ("/wp-admin/", "WordPress Admin Panel"),
                ("/server-status", "Apache Server Status"),
                ("/actuator", "Spring Boot Actuator"),
                ("/api/swagger", "Swagger UI Exposed"),
                ("/.env", "Environment File Exposed"),
                ("/config.php", "Config File Exposed"),
                ("/backup.zip", "Backup Archive Exposed"),
            ]

            tasks = []
            for path, _ in sensitive_paths:
                tasks.append(client.get(base + path))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            endpoints_checked += len(tasks)

            for (path, label), result in zip(sensitive_paths, results):
                if isinstance(result, Exception):
                    continue
                code = result.status_code
                if code in (200, 301, 302):
                    sev = "critical" if path in ("/.env", "/.git/HEAD", "/config.php") else \
                          "high"    if path in ("/admin", "/wp-admin/", "/actuator", "/phpinfo.php") else \
                          "medium"  if code == 200 else "info"
                    cvss = 9.1 if sev=="critical" else 7.2 if sev=="high" else 5.0 if sev=="medium" else 2.0
                    all_findings.append({
                        "severity": sev,
                        "type": f"Exposed Path: {label}",
                        "url": base + path,
                        "param": "-",
                        "method": "Path Discovery",
                        "cvss": cvss,
                        "status": "open",
                        "desc": f"HTTP {code} returned for {path}. {label} may be accessible.",
                        "remediation": f"Restrict access to {path} or remove the file/directory."
                    })

            # ── Check HTTPS redirect from HTTP ────────────────────────────
            if final_url.startswith("https://"):
                try:
                    http_url = final_url.replace("https://", "http://", 1)
                    http_resp = await client.get(http_url, follow_redirects=False)
                    endpoints_checked += 1
                    if http_resp.status_code not in (301, 302, 307, 308):
                        all_findings.append({
                            "severity": "high",
                            "type": "HTTP Not Redirected to HTTPS",
                            "url": http_url,
                            "param": "-",
                            "method": "Protocol Check",
                            "cvss": 6.5,
                            "status": "open",
                            "desc": "HTTP requests are not redirected to HTTPS. Data can be intercepted.",
                            "remediation": "Configure a 301 redirect from HTTP to HTTPS."
                        })
                except Exception:
                    pass

    except httpx.ConnectError:
        raise HTTPException(status_code=400, detail=f"Cannot connect to {raw_url}. Target may be unreachable.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail=f"Request timed out connecting to {raw_url}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan error: {str(e)}")

    # Deduplicate
    seen = set()
    unique_findings = []
    for f in all_findings:
        key = (f["type"], f["url"])
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    # Assign sequential IDs
    for i, f in enumerate(unique_findings, 1):
        f["id"] = i

    elapsed = round(time.time() - start, 2)
    risk = compute_risk_score(unique_findings)

    return {
        "url": raw_url,
        "final_url": final_url if 'final_url' in dir() else raw_url,
        "status": "completed",
        "findings": unique_findings,
        "risk_score": risk,
        "endpoints_checked": endpoints_checked,
        "scan_time_seconds": elapsed,
    }


# ── Kept for compatibility ───────────────────────────────────────────────────
@router.get("/{scan_id}")
async def get_scan_status(scan_id: int):
    return {"scan_id": scan_id, "status": "completed"}
