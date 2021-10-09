API container
-----------
Run the script `run.sh` to launch the API container. This takes one comamnd-line argument specifying the base directory (examples: '/', '.', etc)
The script creates the image from the Dockerfile and lauches the container with the server endpoint http://localhost:5000, returning the container ID
To make requests:  1) get a shell on the conatiner with: `docker exec -it <container_id> /bin/bash`, 
                   2) list the contents of the base directory with `curl http://localhost:5000`,
                   3) list the contents of other directories/files relative to the base directory with `curl http://localhost:5000/<path>`


Unit Testing
--------------
Run the script `run_tests.sh` to run unit tests.
Unit tests are contained in the file `tst/server.py` and use the `pytest` framework