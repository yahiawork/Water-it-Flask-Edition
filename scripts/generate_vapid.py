"""Generate VAPID keys for Web Push.

Run:
  python scripts/generate_vapid.py

Then copy values into .env:
  VAPID_PUBLIC_KEY=...
  VAPID_PRIVATE_KEY=...
"""

from __future__ import annotations

try:
    # Provided by the pywebpush dependency (py-vapid)
    from py_vapid import Vapid01
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "py_vapid was not found. Make sure you installed requirements.txt.\n"
        f"Original error: {e}"
    )


def main():
    v = Vapid01()
    v.generate_keys()
    # py_vapid exposes keys as URL-safe base64 strings
    print("VAPID_PUBLIC_KEY=" + v.public_key)
    print("VAPID_PRIVATE_KEY=" + v.private_key)


if __name__ == '__main__':
    main()
