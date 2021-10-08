from flask import Flask, jsonify
from markupsafe import escape
from pathlib import Path
import os

app = Flask(__name__)
BASE_DIR = os.getenv('BASE_DIR')

@app.route('/')
def index():
    return getContents(Path(BASE_DIR))

@app.route('/<path:subpath>')
def get(subpath):
    base_path = Path(BASE_DIR)
    return getContents(Path(str(base_path)  +  escape(subpath)))

# path is an Path object
def getContents(path):
    if not path.exists():
        return jsonify(f'The specified file or directory {path} does not exist')
    if path.is_file():
        return jsonify(path.read_text())
    else:
        results = map(lambda x: (x, x.stat()), path.iterdir())
        return jsonify(list(map(lambda x: {'name': x[0].name, 'path': str(x[0]), 'is_dir': x[0].is_dir(), 
                                           'owner': x[0].owner(), 'permissions': oct(x[1].st_mode)[-3:], 'size (bytes)': x[1].st_size}, results))) 
        
