"""
Deploy AikApply to a Hugging Face Space (Docker SDK).

Usage (from the project root, with the backend venv):
    backend-fyp/aikapply/venv/bin/python deploy/deploy_hf.py

Reads from backend-fyp/aikapply/.env:
    HF_TOKEN        Hugging Face write token
    DATABASE_URL    Postgres connection string (e.g. Neon)
    GEMINI_API_KEY  Google Gemini key
On the first run it also generates and saves DEPLOY_DJANGO_SECRET_KEY and
DEPLOY_ADMIN_PASSWORD to .env, so they stay the same on later deploys.

Only files tracked by git (git archive HEAD) are uploaded — never .env, the
local database or media uploads. Commit your changes before deploying.
"""
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import dotenv_values
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / "backend-fyp" / "aikapply" / ".env"
SPACE_NAME = "aikapply"
ADMIN_EMAIL = "admin@aikapply.com"

SPACE_HEADER = """---
title: AikApply
emoji: 🎓
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
short_description: AI-assisted university admissions for Pakistani students
---

"""


def ensure_env_value(env: dict, key: str, generate) -> str:
    """Return env[key], generating and appending it to .env if missing."""
    if env.get(key):
        return env[key]
    value = generate()
    with open(ENV_FILE, "a") as f:
        f.write(f"\n{key}={value}\n")
    env[key] = value
    print(f"Generated {key} and saved it to .env")
    return value


def main():
    env = dict(dotenv_values(ENV_FILE))
    missing = [k for k in ("HF_TOKEN", "DATABASE_URL", "GEMINI_API_KEY") if not env.get(k)]
    if missing:
        sys.exit(f"Missing in {ENV_FILE}: {', '.join(missing)}")

    if subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip():
        print("⚠️  You have uncommitted changes — only committed files are deployed.")

    api = HfApi(token=env["HF_TOKEN"])
    username = api.whoami()["name"]
    space_id = f"{username}/{SPACE_NAME}"
    host = re.sub(r"[^a-z0-9-]", "-", f"{username}-{SPACE_NAME}".lower()) + ".hf.space"
    print(f"Deploying to https://huggingface.co/spaces/{space_id}  (app: https://{host})")

    api.create_repo(space_id, repo_type="space", space_sdk="docker", exist_ok=True, private=False)

    # Public settings
    api.add_space_variable(space_id, "DJANGO_ALLOWED_HOSTS", f"{host},localhost,127.0.0.1")
    api.add_space_variable(space_id, "DJANGO_CSRF_TRUSTED_ORIGINS", f"https://{host}")

    # Secrets (never shown publicly)
    django_secret = ensure_env_value(env, "DEPLOY_DJANGO_SECRET_KEY", lambda: secrets.token_urlsafe(50))
    admin_password = ensure_env_value(env, "DEPLOY_ADMIN_PASSWORD", lambda: secrets.token_urlsafe(12))
    for key, value in {
        "GEMINI_API_KEY": env["GEMINI_API_KEY"],
        "DATABASE_URL": env["DATABASE_URL"],
        "DJANGO_SECRET_KEY": django_secret,
        "DJANGO_SUPERUSER_EMAIL": ADMIN_EMAIL,
        "DJANGO_SUPERUSER_PASSWORD": admin_password,
    }.items():
        api.add_space_secret(space_id, key, value)
    print("Space variables and secrets set")

    # Stage committed files only, with the Space's README header added
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=archive, check=True)
        readme = Path(tmp) / "README.md"
        readme.write_text(SPACE_HEADER + readme.read_text())

        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True).stdout.strip()
        api.upload_folder(
            folder_path=tmp,
            repo_id=space_id,
            repo_type="space",
            commit_message=f"Deploy {commit}",
            delete_patterns="*",  # remove files that no longer exist in the project
        )

    print(f"\n✅ Uploaded. Hugging Face is now building the container (5–10 minutes).")
    print(f"   Build logs: https://huggingface.co/spaces/{space_id}?logs=build")
    print(f"   App:        https://{host}")
    print(f"   Admin:      {ADMIN_EMAIL}  (password: DEPLOY_ADMIN_PASSWORD in .env)")


if __name__ == "__main__":
    main()
