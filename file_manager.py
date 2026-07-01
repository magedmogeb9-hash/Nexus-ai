import os
import shutil
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv', 'json', 'jsonl', 'txt', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, upload_folder, user_id):
    if not file or not allowed_file(file.filename):
        return None, "File type not allowed"
    filename = secure_filename(file.filename)
    user_dir = os.path.join(upload_folder, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    path = os.path.join(user_dir, filename)
    file.save(path)
    return path, None

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
