"""
Deploy AikApply to Render (free web service, Docker) from the public GitHub repo.

Usage (from the project root, with the backend venv):
    backend-fyp/aikapply/venv/bin/python deploy/deploy_render.py

Reads from backend-fyp/aikapply/.env:
    RENDER_API_KEY  Render API key (Account Settings → API Keys)
    DATABASE_URL    Postgres connection string (e.g. Neon)
    GEMINI_API_KEY  Google Gemini key
On the first run it also generates and saves DEPLOY_DJANGO_SECRET_KEY and
DEPLOY_ADMIN_PASSWORD to .env, so they stay the same on later deploys.

Render builds the Dockerfile from GitHub, so push your commits first.
After the first deploy, every push to main redeploys automatically.
"""
import secrets
import sys
import time
from pathlib import Path

import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / "backend-fyp" / "aikapply" / ".env"
API = "https://api.render.com/v1"
SERVICE_NAME = "aikapply"
REPO = "https://github.com/Muaaz-Butt/AikApply"
ADMIN_EMAIL = "admin@aikapply.com"


def ensure_env_value(env: dict, key: str, generate) -> str:
    if env.get(key):
        return env[key]
    value = generate()
    with open(ENV_FILE, "a") as f:
        f.write(f"\n{key}={value}\n")
    env[key] = value
    print(f"Generated {key} and saved it to .env")
    return value


def call(method, path, key, **kwargs):
    r = requests.request(method, f"{API}{path}", headers={
        "Authorization": f"Bearer {key}", "Accept": "application/json",
    }, timeout=60, **kwargs)
    if r.status_code >= 400:
        sys.exit(f"Render API {method} {path} failed: {r.status_code} {r.text[:500]}")
    return r.json() if r.text else {}


def main():
    env = dict(dotenv_values(ENV_FILE))
    missing = [k for k in ("RENDER_API_KEY", "DATABASE_URL", "GEMINI_API_KEY") if not env.get(k)]
    if missing:
        sys.exit(f"Missing in {ENV_FILE}: {', '.join(missing)}")
    key = env["RENDER_API_KEY"]

    env_vars = {
        # The free plan (512 MB) can't run the auto-apply browser; keep memory low
        "AUTO_APPLY_ENABLED": "0",
        "WEB_WORKERS": "1",
        "DJANGO_ALLOWED_HOSTS": ".onrender.com,localhost,127.0.0.1",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.onrender.com",
        "GEMINI_API_KEY": env["GEMINI_API_KEY"],
        "DATABASE_URL": env["DATABASE_URL"],
        "DJANGO_SECRET_KEY": ensure_env_value(env, "DEPLOY_DJANGO_SECRET_KEY", lambda: secrets.token_urlsafe(50)),
        "DJANGO_SUPERUSER_EMAIL": ADMIN_EMAIL,
        "DJANGO_SUPERUSER_PASSWORD": ensure_env_value(env, "DEPLOY_ADMIN_PASSWORD", lambda: secrets.token_urlsafe(12)),
    }
    env_list = [{"key": k, "value": v} for k, v in env_vars.items()]

    existing = [s["service"] for s in call("GET", f"/services?name={SERVICE_NAME}&limit=20", key)
                if s["service"]["name"] == SERVICE_NAME]
    if existing:
        service = existing[0]
        print(f"Updating existing service {service['id']}")
        call("PUT", f"/services/{service['id']}/env-vars", key, json=env_list)
        call("POST", f"/services/{service['id']}/deploys", key, json={"clearCache": "do_not_clear"})
    else:
        owners = call("GET", "/owners?limit=20", key)
        owner_id = owners[0]["owner"]["id"]
        print(f"Creating web service '{SERVICE_NAME}' from {REPO}")
        created = call("POST", "/services", key, json={
            "type": "web_service",
            "name": SERVICE_NAME,
            "ownerId": owner_id,
            "repo": REPO,
            "branch": "main",
            "autoDeploy": "yes",
            "envVars": env_list,
            "serviceDetails": {
                "runtime": "docker",
                "plan": "free",
                "region": "singapore",
                "healthCheckPath": "/api/deadlines/summary/",
                "envSpecificDetails": {"dockerfilePath": "./Dockerfile", "dockerContext": "."},
            },
        })
        service = created.get("service", created)

    url = service.get("serviceDetails", {}).get("url", "")
    print(f"Service: https://dashboard.render.com/web/{service['id']}")
    print(f"App:     {url}")

    if "--wait" in sys.argv:
        print("Waiting for the deploy (first build takes ~10 minutes)...")
        last = None
        while True:
            deploys = call("GET", f"/services/{service['id']}/deploys?limit=1", key)
            status = deploys[0]["deploy"]["status"] if deploys else "pending"
            if status != last:
                print(f"  deploy status: {status}", flush=True)
                last = status
            if status in ("live", "build_failed", "update_failed", "canceled", "deactivated"):
                break
            time.sleep(20)
        if last != "live":
            sys.exit(f"Deploy ended with status '{last}' — check the logs in the Render dashboard.")

    print(f"\nAdmin login: {ADMIN_EMAIL}  (password: DEPLOY_ADMIN_PASSWORD in .env)")


if __name__ == "__main__":
    main()
