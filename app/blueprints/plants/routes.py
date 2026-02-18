from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import NotFound

from ... import db
from ...forms import PlantForm, ReminderForm
from ...models import Plant, PlantPhoto, Reminder
from ...utils import save_upload
from ...notifications import compute_next_run

bp = Blueprint('plants', __name__)


def _get_plant_or_404(plant_id: int) -> Plant:
    plant = Plant.query.get(int(plant_id))
    if not plant:
        raise NotFound()
    return plant


@bp.get('/')
def list_plants():
    view = request.args.get('view', 'grid')  # grid | list | single
    plants = Plant.query.order_by(Plant.created_at.desc()).all()
    return render_template('plants/list.html', plants=plants, view=view)


@bp.route('/add', methods=['GET', 'POST'])
def add_plant():
    form = PlantForm()
    if form.validate_on_submit():
        plant = Plant(
            name=form.name.data,
            scientific_name=form.scientific_name.data,
            origin=form.origin.data,
            age_months=form.age_months.data,
            light=form.light.data,
            water=form.water.data,
            soil=form.soil.data,
            notes=form.notes.data,
        )
        db.session.add(plant)
        db.session.commit()

        # Save photos
        files = form.photos.data or []
        for f in files:
            if not f or not getattr(f, 'filename', ''):
                continue
            try:
                filename = save_upload(f, current_app.config['UPLOAD_FOLDER'])
                db.session.add(PlantPhoto(plant_id=plant.id, filename=filename))
            except Exception as e:
                flash(str(e), 'error')
        db.session.commit()

        flash('Plant added.', 'success')
        return redirect(url_for('plants.detail', plant_id=plant.id))

    return render_template('plants/add.html', form=form)


@bp.route('/<int:plant_id>', methods=['GET', 'POST'])
def detail(plant_id: int):
    plant = _get_plant_or_404(plant_id)

    reminder_form = ReminderForm(prefix='rem')
    if reminder_form.validate_on_submit() and request.form.get('form_name') == 'reminder':
        from datetime import datetime
        today = datetime.utcnow().date()
        rem = Reminder(
            plant_id=plant.id,
            interval_text=reminder_form.interval_text.data,
            time_of_day=reminder_form.time_of_day.data,
            start_date=today,
        )
        rem.next_run_at = compute_next_run(rem.interval_text, rem.time_of_day, start=today)
        db.session.add(rem)
        db.session.commit()
        flash('Reminder added.', 'success')
        return redirect(url_for('plants.detail', plant_id=plant.id))

    return render_template('plants/detail.html', plant=plant, reminder_form=reminder_form)


@bp.route('/<int:plant_id>/edit', methods=['GET', 'POST'])
def edit(plant_id: int):
    plant = _get_plant_or_404(plant_id)
    form = PlantForm(obj=plant)

    if form.validate_on_submit():
        form.populate_obj(plant)
        db.session.commit()

        # optional new photos
        files = form.photos.data or []
        for f in files:
            if not f or not getattr(f, 'filename', ''):
                continue
            try:
                filename = save_upload(f, current_app.config['UPLOAD_FOLDER'])
                db.session.add(PlantPhoto(plant_id=plant.id, filename=filename))
            except Exception as e:
                flash(str(e), 'error')
        db.session.commit()

        flash('Plant updated.', 'success')
        return redirect(url_for('plants.detail', plant_id=plant.id))

    return render_template('plants/edit.html', form=form, plant=plant)


@bp.post('/<int:plant_id>/delete')
def delete(plant_id: int):
    plant = _get_plant_or_404(plant_id)
    db.session.delete(plant)
    db.session.commit()
    flash('Plant deleted.', 'success')
    return redirect(url_for('plants.list_plants'))


@bp.post('/<int:plant_id>/photos/add')
def add_photos(plant_id: int):
    plant = _get_plant_or_404(plant_id)
    files = request.files.getlist('photos')
    if not files:
        flash('No files selected.', 'error')
        return redirect(url_for('plants.detail', plant_id=plant.id))

    for f in files:
        if not f or not getattr(f, 'filename', ''):
            continue
        try:
            filename = save_upload(f, current_app.config['UPLOAD_FOLDER'])
            db.session.add(PlantPhoto(plant_id=plant.id, filename=filename))
        except Exception as e:
            flash(str(e), 'error')
    db.session.commit()
    flash('Photos uploaded.', 'success')
    return redirect(url_for('plants.detail', plant_id=plant.id))


@bp.post('/photos/<int:photo_id>/delete')
def delete_photo(photo_id: int):
    photo = PlantPhoto.query.get(int(photo_id))
    if not photo:
        raise NotFound()
    plant_id = photo.plant_id

    # remove file
    try:
        import os
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

    db.session.delete(photo)
    db.session.commit()
    flash('Photo deleted.', 'success')
    return redirect(url_for('plants.detail', plant_id=plant_id))


@bp.post('/reminders/<int:reminder_id>/delete')
def delete_reminder(reminder_id: int):
    rem = Reminder.query.get(int(reminder_id))
    if not rem:
        raise NotFound()
    plant_id = rem.plant_id
    db.session.delete(rem)
    db.session.commit()
    flash('Reminder deleted.', 'success')
    return redirect(url_for('plants.detail', plant_id=plant_id))
