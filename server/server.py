from flask import Flask, jsonify, request
from markupsafe import escape
from pathlib import Path
import os

app = Flask(__name__)
BASE_DIR = os.getenv('BASE_DIR')
BASE_DIR = '.' if BASE_DIR is None else BASE_DIR

ERR_MSG = 'The specified file or directory {} does not exist'
DELETE_MSG = 'Successfully deleted the specified file or directory {}'
DELETE_ERR_MSG = 'The specified directory {} is not empty'
CREATE_EXISTS_MSG = 'The specified file or directory {} already exists'
CREATE_REQ_ERR_MSG = 'The request json for the create request is missing required fields'
RENAME_REQ_ERR_MSG = 'The request json for the rename request is missing required fields'
CREATE_MSG = 'Successfully created the specified file or directory {}'
RENAME_MSG = 'Successfully renamed the specified file or directory {} to {}'
RENAME_EXISTS_MSG = 'The new name for the file or directory {} already exists'

def create_app(base_dir=None):
    global app
    global BASE_DIR
    if base_dir is not None:
        BASE_DIR = base_dir
    return app

# get the contents of the filesystem root
@app.route('/', methods=['GET'])
def index():
    return jsonify(getContents(Path(BASE_DIR)))
        

# get the contents of a directory or a file other than the root
@app.route('/<path:subpath>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def processRequest(subpath):
    path = Path(Path(BASE_DIR), escape(subpath))
    if request.method == "GET":
        return jsonify(getContents(path))
    elif request.method == 'DELETE':
        return jsonify(deleteContents(path))
    elif request.method == 'PUT':
        return jsonify(create(path, request.json))
    elif request.method == 'POST':
        return jsonify(rename(path, request.json))

def create(path, request):
    if ("is_dir" not in request) or (request["is_dir"] == "False" and "text" not in request):
        return CREATE_REQ_ERR_MSG
    if path.exists():
        return CREATE_EXISTS_MSG.format(path)
    if request["is_dir"] == "True":
        path.mkdir(parents=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(request["text"])
    return CREATE_MSG.format(path)

def rename(path, request):
    if ("new_name" not in request):
        return RENAME_REQ_ERR_MSG
    if not path.exists():
        return ERR_MSG.format(path)
    newpath = path.parent / request["new_name"]
    if newpath.exists():
        return RENAME_EXISTS_MSG.format(newpath)
    path.rename(newpath)
    return RENAME_MSG.format(path, newpath)

def deleteContents(path):
    if not path.exists():
        return ERR_MSG.format(path)
    if path.is_file():
        path.unlink()
    elif any(path.iterdir()):
        return DELETE_ERR_MSG.format(path)
    else:
        path.rmdir()
    return DELETE_MSG.format(path)

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
        
