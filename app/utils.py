import os
import secrets
from werkzeug.utils import secure_filename

ALLOWED_EXT = {'.png', '.jpg', '.jpeg', '.webp'}


def save_upload(file_storage, upload_folder: str) -> str:
    filename = secure_filename(file_storage.filename or '')
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXT:
        raise ValueError('Unsupported file type. Use PNG/JPG/WEBP.')

    token = secrets.token_hex(12)
    final_name = f"{token}{ext}"
    path = os.path.join(upload_folder, final_name)
    file_storage.save(path)
    return final_name
