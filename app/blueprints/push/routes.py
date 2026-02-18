from __future__ import annotations

import os
from flask import jsonify, request

from ... import db, csrf
from ...models import PushSubscription

from . import bp


@bp.get('/vapid-public-key')
def vapid_public_key():
    key = os.getenv('VAPID_PUBLIC_KEY', '').strip()
    return jsonify({'key': key})


@bp.post('/subscribe')
@csrf.exempt
def subscribe():
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()
    keys = data.get('keys') or {}
    p256dh = (keys.get('p256dh') or '').strip()
    auth = (keys.get('auth') or '').strip()

    if not endpoint or not p256dh or not auth:
        return jsonify({'ok': False, 'error': 'Invalid subscription payload.'}), 400

    sub = PushSubscription.query.filter_by(endpoint=endpoint).first()
    if sub:
        sub.p256dh = p256dh
        sub.auth = auth
    else:
        sub = PushSubscription(endpoint=endpoint, p256dh=p256dh, auth=auth)
        db.session.add(sub)
    db.session.commit()
    return jsonify({'ok': True})


@bp.post('/unsubscribe')
@csrf.exempt
def unsubscribe():
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()
    if not endpoint:
        return jsonify({'ok': False, 'error': 'Missing endpoint.'}), 400
    sub = PushSubscription.query.filter_by(endpoint=endpoint).first()
    if sub:
        db.session.delete(sub)
        db.session.commit()
    return jsonify({'ok': True})
