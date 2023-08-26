#!/bin/bash -ex

docker build -t app --target app .

# We can either craete a volume inside a service container 
# that will be persisted between rebuilds and runs using
docker volume create db
docker run --rm -it -p 8000:8000 -v db:/db app
# Which creates /var/lib/docker/volumes/db/_data

# Or map local directory to be mapped to a docker volume
# e.g /Users/nikodemkirsz/Projects/fast-library/db similary to how logs
# are stored

# docker run --rm -it -p 8000:8000 -v "${PWD}/db:/db:rw" app

