from datetime import datetime
from flask import Blueprint, current_app, render_template, request
import requests

from ...models import Plant, Reminder

bp = Blueprint('home', __name__)

# small in-process cache to reduce API calls
_WEATHER_CACHE: dict[str, tuple[float, dict]] = {}


def _weather_icon_for(main: str, clouds: int | None = None):
    # Map OpenWeather conditions to our SVG assets.
    main = (main or '').lower()
    if 'rain' in main or 'drizzle' in main or 'thunder' in main:
        return 'assets/images/weather/rainy.svg'
    if 'cloud' in main:
        if clouds is not None and clouds < 40:
            return 'assets/images/weather/cloudy_sun.svg'
        return 'assets/images/weather/cloudy.svg'
    return 'assets/images/weather/sun.svg'


def fetch_weather_slots(city: str):
    api_key = current_app.config.get('OPENWEATHER_API_KEY', '')
    if not api_key:
        return {
            'ok': False,
            'city': city,
            'country': '',
            'slots': [],
            'error': 'OPENWEATHER_API_KEY not set.'
        }

    # Cache for 10 minutes
    import time
    k = (city or '').strip().lower()
    hit = _WEATHER_CACHE.get(k)
    if hit and (time.time() - hit[0]) < 600:
        return hit[1]

    # Use 5 day / 3 hour forecast
    url = 'https://api.openweathermap.org/data/2.5/forecast'
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    city_name = data.get('city', {}).get('name', city)
    country = data.get('city', {}).get('country', '')

    slots = []
    for item in data.get('list', [])[:8]:  # first 24h-ish
        dt = datetime.fromtimestamp(item.get('dt', 0))
        temp = round(item.get('main', {}).get('temp', 0))
        main = (item.get('weather') or [{}])[0].get('main', '')
        clouds = item.get('clouds', {}).get('all')
        slots.append({
            'label': dt.strftime('%a %I %p').replace(' 0', ' '),
            'temp': temp,
            'icon': _weather_icon_for(main, clouds)
        })
        if len(slots) == 3:
            break

    result = {
        'ok': True,
        'city': city_name,
        'country': country,
        'slots': slots,
        'error': None
    }

    _WEATHER_CACHE[k] = (time.time(), result)
    return result


@bp.get('/')
def index():
    city = request.args.get('city') or current_app.config.get('DEFAULT_CITY', 'San Francisco')

    weather = None
    error = None
    try:
        weather = fetch_weather_slots(city)
        if not weather['ok']:
            error = weather['error']
    except Exception as e:
        weather = {'ok': False, 'city': city, 'country': '', 'slots': [], 'error': str(e)}
        error = str(e)

    # Next reminder = simplest: latest reminder + plant
    reminder_cards = []
    reminders = Reminder.query.order_by(Reminder.created_at.desc()).limit(5).all()
    for rem in reminders:
        plant = Plant.query.get(rem.plant_id)
        if not plant:
            continue
        reminder_cards.append({
            'plant_name': plant.name,
            'interval': rem.interval_text,
            'time': rem.time_of_day,
            'plant_id': plant.id
        })

    return render_template('home.html', weather=weather, error=error, reminder_cards=reminder_cards)
