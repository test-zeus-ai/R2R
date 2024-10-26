#!/bin/bash
set -ex
r2r-full docker-down ||:
docker rmi r2r-r2r ||:
r2r serve --docker --build ||:
