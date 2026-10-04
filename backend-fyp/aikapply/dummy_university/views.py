"""
Demo university admission portals for testing auto-apply locally.

GET  /demo-portals/<slug>/          → the portal's application form
POST /demo-portals/<slug>/submit/   → stores the submission and shows what was received
GET  /demo-portals/submissions/     → every submission received so far (newest first)

Submissions are saved to media/dummy_submissions/<slug>/<timestamp>.json
"""
import json
from datetime import datetime
from html import escape
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

PORTALS_DIR = Path(__file__).resolve().parent / "portals"

PORTALS = {
    "air-university": "Air University",
    "uet-lahore":     "UET Lahore",
    "fast-nuces":     "FAST NUCES",
    "bahria":         "Bahria University",
}


def _submissions_dir() -> Path:
    return Path(settings.MEDIA_ROOT) / "dummy_submissions"


def _page(title: str, body: str) -> HttpResponse:
    css = (PORTALS_DIR / "portal.css").read_text()
    return HttpResponse(
        f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        f"<title>{escape(title)}</title><style>{css}</style></head>"
        f"<body><div class='form-container'>{body}</div></body></html>"
    )


def portal(request, slug):
    if slug not in PORTALS:
        raise Http404("Unknown demo portal")
    html = (PORTALS_DIR / f"{slug}.html").read_text()
    css = (PORTALS_DIR / "portal.css").read_text()
    return HttpResponse(html.replace("/*PORTAL_CSS*/", css))


@csrf_exempt
def submit(request, slug):
    if slug not in PORTALS:
        raise Http404("Unknown demo portal")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    fields = {key: request.POST.get(key, "") for key in request.POST.keys()}
    files = {
        key: {"name": f.name, "size_kb": round(f.size / 1024, 1)}
        for key, f in request.FILES.items()
    }

    received_at = datetime.now()
    record = {
        "portal": slug,
        "university": PORTALS[slug],
        "received_at": received_at.isoformat(timespec="seconds"),
        "fields": fields,
        "files": files,
    }
    out_dir = _submissions_dir() / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{received_at:%Y%m%d_%H%M%S_%f}.json").write_text(json.dumps(record, indent=2))

    filled = sum(1 for v in fields.values() if v.strip())
    rows = "".join(
        f"<tr><td>{escape(k)}</td><td>{escape(v) if v.strip() else '<span class=empty>— not filled —</span>'}</td></tr>"
        for k, v in fields.items()
    )
    file_rows = "".join(
        f"<tr><td>{escape(k)}</td><td>📎 {escape(v['name'])} ({v['size_kb']} KB)</td></tr>"
        for k, v in files.items()
    ) or "<tr><td colspan=2><span class=empty>No files uploaded</span></td></tr>"

    return _page(
        f"{PORTALS[slug]} — Application Received",
        f"<div class='success-banner'>✅ Application received by {escape(PORTALS[slug])}</div>"
        f"<p class='muted'>{filled} of {len(fields)} fields filled · {len(files)} file(s) · "
        f"{received_at:%d %b %Y, %I:%M %p}</p>"
        f"<h3>Submitted fields</h3><table>{rows}</table>"
        f"<h3>Uploaded documents</h3><table>{file_rows}</table>"
        f"<p class='muted'>All submissions: <a href='/demo-portals/submissions/'>/demo-portals/submissions/</a></p>",
    )


def submissions(request):
    records = []
    base = _submissions_dir()
    if base.exists():
        for path in base.glob("*/*.json"):
            try:
                records.append(json.loads(path.read_text()))
            except (OSError, json.JSONDecodeError):
                continue
    records.sort(key=lambda r: r.get("received_at", ""), reverse=True)

    if not records:
        body = "<h2>Demo Portal Submissions</h2><p class='muted'>No applications received yet.</p>"
    else:
        cards = []
        for r in records:
            fields = r.get("fields", {})
            filled = sum(1 for v in fields.values() if str(v).strip())
            rows = "".join(
                f"<tr><td>{escape(k)}</td><td>{escape(str(v)) if str(v).strip() else '<span class=empty>— not filled —</span>'}</td></tr>"
                for k, v in fields.items()
            )
            rows += "".join(
                f"<tr><td>{escape(k)}</td><td>📎 {escape(v['name'])}</td></tr>"
                for k, v in r.get("files", {}).items()
            )
            cards.append(
                f"<details><summary><b>{escape(r.get('university', ''))}</b> · {escape(r.get('received_at', ''))} · "
                f"{filled}/{len(fields)} fields · {len(r.get('files', {}))} file(s)</summary><table>{rows}</table></details>"
            )
        body = f"<h2>Demo Portal Submissions</h2><p class='muted'>{len(records)} received, newest first.</p>" + "".join(cards)
    return _page("Demo Portal Submissions", body)
