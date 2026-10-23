import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOOD_KEY = "k" * 60
PROD_ENV = {
    "DEBUG": "False",
    "SECRET_KEY": GOOD_KEY,
    "ALLOWED_HOSTS": "example.com",
    "DB_NAME": "db",
    "DB_USER": "user",
    "DB_PASSWORD": "pw",  # pragma: allowlist secret
    "DB_HOST": "localhost",
    "SMTP_HOST": "smtp.example.com",
}


def load_settings(**env):
    # A clean environment, so a developer's own .env values do not leak in.
    clean = {k: v for k, v in os.environ.items() if k in {"PATH", "HOME"}}
    code = "import kamikon.settings as s; print(s.SECURE_SSL_REDIRECT, s.SESSION_COOKIE_SECURE)"
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env={**clean, **env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_settings_enable_https_flags():
    result = load_settings(**PROD_ENV)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "True True"


def test_debug_settings_allow_blank_secret_key():
    result = load_settings(**{**PROD_ENV, "DEBUG": "True", "SECRET_KEY": ""})
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False False"


def test_weak_secret_key_is_rejected():
    result = load_settings(**{**PROD_ENV, "SECRET_KEY": "short"})
    assert "ImproperlyConfigured" in result.stderr


def test_insecure_prefix_secret_key_is_rejected():
    result = load_settings(**{**PROD_ENV, "SECRET_KEY": "django-insecure-" + "k" * 60})
    assert "ImproperlyConfigured" in result.stderr


def test_empty_allowed_hosts_is_rejected_in_production():
    result = load_settings(**{**PROD_ENV, "ALLOWED_HOSTS": ""})
    assert "ImproperlyConfigured" in result.stderr


def test_missing_database_setting_is_rejected_in_production():
    env = {k: v for k, v in PROD_ENV.items() if k != "DB_PASSWORD"}
    result = load_settings(**env)
    assert "ImproperlyConfigured" in result.stderr
