from flask import Flask, jsonify
from markupsafe import escape
from pathlib import Path
import os

app = Flask(__name__)
BASE_DIR = os.getenv('BASE_DIR')
BASE_DIR = '.' if BASE_DIR is None else BASE_DIR

ERR_MSG = 'The specified file or directory {} does not exist'

def create_app(base_dir=None):
    global app
    global BASE_DIR
    if base_dir is not None:
        BASE_DIR = base_dir
    return app

# get the contents of the filesystem root
@app.route('/')
def index():
    return jsonify(getContents(Path(BASE_DIR)))

# get the contents of a directory or a file other than the root
@app.route('/<path:subpath>')
def get(subpath):
    return jsonify(getContents(Path(Path(BASE_DIR), escape(subpath))))

# return contents in a list format
# path is an Path object
def getContents(path):
    if not path.exists():
        return ERR_MSG.format(path)
    if path.is_file():
        return path.read_text()
    else:
        results = map(lambda x: (x, x.stat()), path.iterdir())
        return list(map(lambda x: {'name': x[0].name, 'path': str(x[0]), 'is_dir': x[0].is_dir(), 
                                   'owner': x[0].owner(), 'permissions': oct(x[1].st_mode)[-3:], 'size (bytes)': x[1].st_size}, results))
        
