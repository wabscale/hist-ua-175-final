#!/bin/sh

docker run --rm -dit -p 9080:9080 -p 8080:8080 -v ~/dgraph:/dgraph dgraph/standalone
docker run --rm -dit -p 8000:8000 dgraph/ratel

echo 'http://localhost:8000'
