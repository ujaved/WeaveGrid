Simple CRUD API for the filesystem
-----------------------------------

CRUD REST API for a portion of user's filesystem, with the user specifying a root directory.

Run API server
--------------
Run the script `run.sh` to launch the API container. This takes one comamnd-line argument specifying the root directory, for example: `./run.sh '/'` or `./run.sh '.'`
The script creates the image from the Dockerfile and lauches the container with the server endpoint http://localhost:5000, returning the container ID.

Make Requests
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
Unit tests are contained in the file `tst/server.py` and use the `pytest` framework.