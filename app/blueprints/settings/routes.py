import json
import os
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

bp = Blueprint('settings', __name__)


def _settings_path():
    instance_dir = os.path.join(current_app.root_path, '..', 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    return os.path.join(instance_dir, 'settings.json')


def load_settings():
    path = _settings_path()
    if not os.path.exists(path):
        return {'default_city': current_app.config.get('DEFAULT_CITY', 'San Francisco')}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_settings(data: dict):
    path = _settings_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@bp.route('/', methods=['GET', 'POST'])
def index():
    settings = load_settings()

    if request.method == 'POST':
        city = (request.form.get('default_city') or '').strip()
        if not city:
            flash('City is required.', 'error')
            return redirect(url_for('settings.index'))

        settings['default_city'] = city
        save_settings(settings)
        flash('Settings saved.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', settings=settings)
