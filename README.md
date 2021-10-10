Simple CRUD API for the filesystem
-----------------------------------

CRUD REST API for a portion of user's filesystem, with the user specifying a root directory.

Run API server
--------------
Run the script `run.sh` to launch the API container. This takes one comamnd-line argument specifying the root directory, for example: `./run.sh '/'` or `./run.sh '.'`
The script creates the image from the Dockerfile and lauches the container with the server endpoint http://localhost:5000, returning the container ID.

API Calls and Requests
---------------
To make requests, get a shell on the conatiner with: `docker exec -it <container_id> /bin/bash`

1. Get contents of root directory: `curl http://localhost:5000`. Note that only a GET method is valid for the root directory.
2. Get contents of a directory or a file <path> relative to the root directory: `curl http://localhost:5000/<path>`
3. Delete a file or an empty directory (other than root): `curl -X DELETE http://localhost:5000/<path>`
4. Create a file or an empty directory (other than root). Note that the service will create all missing directories in the path. 
  - For a file a valid request is: `curl -X PUT -H "Content-Type: application/json" -d '{"is_dir": "False", "text": <string>}' http://localhost:5000/<path> `
  - For a directory a valid request is: `curl -X PUT -H "Content-Type: application/json" -d '{"is_dir": "True"}' http://localhost:5000/<path>`
5. Rename a file or directory (other than root). A valid request is: `curl -X POST -H "Content-Type: application/json" -d '{"new_name": <string>}' http://localhost:5000/<path>`. 
Note that "new_name" is not that absolute path, just a short name. Note also that the new absolute path should not already exist.

Unit Testing
--------------
Run the script `run_tests.sh` to run unit tests.
Unit tests are contained in the file `tst/server.py` and use the `pytest` framework

Example Command Sequence
-------------------------

1. Launch service with current directory as root: `./run.sh '.'`
2. From another terminal window get shell on the container: `docker exec -it <container_id> /bin/bash`
3. Send request to get contents of root directory (which is the application folder in this case): `curl http://localhost:5000`. Expected output:
```
root@2283ee070f76:/app# curl http://localhost:5000
[
  {
    "is_dir": true,
    "name": "__pycache__",
    "owner": "root",
    "path": "__pycache__",
    "permissions": "755",
    "size (bytes)": 4096
  },
  {
    "is_dir": true,
    "name": "tst",
    "owner": "root",
    "path": "tst",
    "permissions": "755",
    "size (bytes)": 4096
  },
  {
    "is_dir": false,
    "name": "__init.py__",
    "owner": "root",
    "path": "__init.py__",
    "permissions": "644",
    "size (bytes)": 0
  },
  {
    "is_dir": false,
    "name": "server.py",
    "owner": "root",
    "path": "server.py",
    "permissions": "644",
    "size (bytes)": 3289
  },
  {
    "is_dir": false,
    "name": "requirements.txt",
    "owner": "root",
    "path": "requirements.txt",
    "permissions": "644",
    "size (bytes)": 13
  }
]
```
4. Send request to get contents of file requirements.txt: `curl http://localhost:5000/requirements.txt`. Expected output:
```
root@2283ee070f76:/app# curl http://localhost:5000/requirements.txt
"Flask==1.1.1\n"
```
5. Delete, followed by create requirements.txt. Expected output:
```
root@2283ee070f76:/app# curl -X DELETE http://localhost:5000/requirements.txt
"Successfully deleted the specified file or directory requirements.txt"
root@2283ee070f76:/app# ls
__init.py__  __pycache__  server.py  tst
root@2283ee070f76:/app# curl -X PUT -H "Content-Type: application/json" -d '{"is_dir": "False", "text": "Flask==1.1.1\n"}' http://localhost:5000/requirements.txt
"Successfully created the specified file or directory requirements.txt"
root@2283ee070f76:/app# ls
__init.py__  __pycache__  requirements.txt  server.py  tst
root@2283ee070f76:/app# cat requirements.txt
Flask==1.1.1
root@2283ee070f76:/app# curl http://localhost:5000/requirements.txt
"Flask==1.1.1\n"
```
6. Rename requirements.txt. Expected output:
```
root@2283ee070f76:/app# curl -X POST -H "Content-Type: application/json" -d '{"new_name": "require.txt"}' http://localhost:5000/requirements.txt
"Successfully renamed the specified file or directory requirements.txt to require.txt"
root@2283ee070f76:/app# ls
__init.py__  __pycache__  require.txt  server.py  tst
``` 