from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta
from pywebpush import webpush, WebPushException

from . import db
from .models import Reminder, Plant, PushSubscription


INTERVAL_RE = re.compile(r"^\s*(\d+)\s*(day|days|week|weeks|month|months)\s*$", re.IGNORECASE)


def parse_interval_to_delta(interval_text: str):
    m = INTERVAL_RE.match((interval_text or '').strip())
    if not m:
        # safe default
        return timedelta(days=7)
    n = int(m.group(1))
    unit = m.group(2).lower()
    if 'day' in unit:
        return timedelta(days=n)
    if 'week' in unit:
        return timedelta(days=7 * n)
    # months: use calendar months (relativedelta)
    return relativedelta(months=n)


def _parse_time_of_day(s: str) -> tuple[int, int]:
    s = (s or '09:00').strip()
    if ':' not in s:
        return 9, 0
    hh, mm = s.split(':', 1)
    try:
        return max(0, min(23, int(hh))), max(0, min(59, int(mm)))
    except Exception:
        return 9, 0


def compute_next_run(interval_text: str, time_of_day: str, start: date | None = None, now: datetime | None = None) -> datetime:
    now = now or datetime.utcnow()
    start = start or now.date()
    hh, mm = _parse_time_of_day(time_of_day)
    candidate = datetime(start.year, start.month, start.day, hh, mm)
    delta = parse_interval_to_delta(interval_text)

    # If already in the past, roll forward until future.
    while candidate <= now:
        if isinstance(delta, relativedelta):
            candidate = candidate + delta
        else:
            candidate = candidate + delta
    return candidate


def _vapid_keys():
    """Load VAPID keys from env or generate (dev) and store under instance/.

    For real deployments, set VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY.
    """
    pub = os.getenv('VAPID_PUBLIC_KEY', '').strip()
    priv = os.getenv('VAPID_PRIVATE_KEY', '').strip()
    subj = os.getenv('VAPID_SUBJECT', 'mailto:admin@example.com').strip()
    return pub, priv, subj


def send_push_to_all(title: str, body: str, url: str = '/') -> dict:
    pub, priv, subj = _vapid_keys()
    if not pub or not priv:
        return {'ok': False, 'sent': 0, 'error': 'VAPID keys not set. See README.'}

    payload = json.dumps({'title': title, 'body': body, 'url': url})
    subs = PushSubscription.query.all()
    sent = 0
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                },
                data=payload,
                vapid_private_key=priv,
                vapid_claims={'sub': subj},
            )
            sent += 1
        except WebPushException:
            # Subscription likely expired; remove it.
            try:
                db.session.delete(sub)
                db.session.commit()
            except Exception:
                db.session.rollback()
        except Exception:
            continue
    return {'ok': True, 'sent': sent, 'error': None}


def tick_reminders():
    """Called by scheduler. Sends due reminder notifications and schedules next run."""
    now = datetime.utcnow()
    due = (
        Reminder.query
        .filter(Reminder.active == True)  # noqa: E712
        .filter(Reminder.next_run_at.isnot(None))
        .filter(Reminder.next_run_at <= now)
        .all()
    )

    for rem in due:
        plant = Plant.query.get(rem.plant_id)
        if not plant:
            continue

        title = f"Reminder: {plant.name}"
        body = f"Scheduled: every {rem.interval_text} at {rem.time_of_day}".strip()

        send_push_to_all(title, body, url=f"/plants/{plant.id}")

        rem.last_sent_at = now
        # roll next run forward
        rem.next_run_at = compute_next_run(rem.interval_text, rem.time_of_day, start=now.date(), now=now)

    if due:
        db.session.commit()
