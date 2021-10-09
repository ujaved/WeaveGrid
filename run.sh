#!/bin/bash

if [ $# -eq 0 ]; then
    echo "No base directory provided"
    exit 1
fi

echo "base directory: $1"

echo "building docker image"
docker build -t wg-image .
 
container_id=`docker run --rm -d -p 5000:5000 -e BASE_DIR=$1 wg-image`
echo "Launched API container on http://localhost:5000 with container id: $container_id"