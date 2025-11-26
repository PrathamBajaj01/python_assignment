from flask import Flask, request, jsonify, render_template
import os
import pathlib
from datetime import datetime
from dotenv import load_dotenv
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import threading

load_dotenv()

app = Flask(__name__, template_folder='templates')

DEFAULT_NOTES_DIR = os.getenv('DEFAULT_NOTES_DIR', '').strip()
if not DEFAULT_NOTES_DIR:
    DEFAULT_NOTES_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'NotepadTracker')

ALLOW_ANY_PATH = os.getenv('ALLOW_ANY_PATH', 'false').lower() == 'true'
ALLOWED_BASE_DIRS_ENV = os.getenv('ALLOWED_BASE_DIRS', '').strip()
if ALLOWED_BASE_DIRS_ENV:
    ALLOWED_BASE_DIRS = [p.strip() for p in ALLOWED_BASE_DIRS_ENV.split(',') if p.strip()]
else:
    ALLOWED_BASE_DIRS = [DEFAULT_NOTES_DIR]

AUTO_COMMIT_AUTHOR_NAME = os.getenv('AUTO_COMMIT_AUTHOR_NAME', 'Notepad Tracker')
AUTO_COMMIT_AUTHOR_EMAIL = os.getenv('AUTO_COMMIT_AUTHOR_EMAIL', 'notepad@example.com')

pathlib.Path(DEFAULT_NOTES_DIR).mkdir(parents=True, exist_ok=True)

file_locks = {}

def get_lock_for_path(path):
    lock = file_locks.get(path)
    if lock is None:
        lock = threading.Lock()
        file_locks[path] = lock
    return lock

def ensure_git_repo(path: pathlib.Path) -> Repo:
    cur = path.resolve()
    for parent in (cur, *cur.parents):
        try:
            return Repo(parent)
        except (InvalidGitRepositoryError, NoSuchPathError):
            continue
    repo = Repo.init(cur.parent)
    try:
        cfg = repo.config_writer()
        cfg.set_value('user', 'name', AUTO_COMMIT_AUTHOR_NAME)
        cfg.set_value('user', 'email', AUTO_COMMIT_AUTHOR_EMAIL)
        cfg.release()
    except Exception:
        pass
    return repo

def sanitize_filename(name: str) -> str:
    name = (name or '').strip()
    return name.replace('/', '_').replace('\\', '_')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/meta', methods=['GET'])
def meta():
    return jsonify({'ok': True, 'default_dir': str(pathlib.Path(DEFAULT_NOTES_DIR).resolve())})

@app.route('/load', methods=['POST'])
def load_file():
    data = request.json or {}
    filename = (data.get('filename') or '').strip()
    if not filename:
        filename = 'note'
    safe = sanitize_filename(filename)
    final_path = pathlib.Path(DEFAULT_NOTES_DIR) / (safe + '.txt')
    try:
        final_path.parent.mkdir(parents=True, exist_ok=True)
        if not final_path.exists():
            final_path.write_text('', encoding='utf-8')
        content = final_path.read_text(encoding='utf-8')
        return jsonify({'ok': True, 'content': content, 'path': str(final_path)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_file():
    data = request.json or {}
    filename = (data.get('filename') or '').strip()
    content = data.get('content', '')
    if not filename:
        filename = 'note'
    safe = sanitize_filename(filename)
    final_path = pathlib.Path(DEFAULT_NOTES_DIR) / (safe + '.txt')
    lock = get_lock_for_path(str(final_path))
    with lock:
        try:
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_text(content, encoding='utf-8')
        except Exception as e:
            return jsonify({'ok': False, 'error': f'Write failed: {e}'}), 500
        try:
            repo = ensure_git_repo(final_path)
            rel_path = str(final_path.relative_to(repo.working_tree_dir))
            repo.index.add([rel_path])
            commit_message = f'Auto-save: {final_path.name} @ {datetime.utcnow().isoformat()}Z'
            try:
                from git import Actor
                author = Actor(AUTO_COMMIT_AUTHOR_NAME, AUTO_COMMIT_AUTHOR_EMAIL)
                repo.index.commit(commit_message, author=author)
            except Exception:
                repo.index.commit(commit_message)
        except Exception as e:
            return jsonify({'ok': True, 'warning': f'Saved file but git commit failed: {e}', 'path': str(final_path)})
    return jsonify({'ok': True, 'path': str(final_path)})

if __name__ == '__main__':
    print(f'Starting Notepad Tracker. Default notes dir: {DEFAULT_NOTES_DIR}')
    app.run(host='127.0.0.1', port=5000, debug=True)
