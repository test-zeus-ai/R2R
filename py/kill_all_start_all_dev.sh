#!/bin/bash
set -ex
r2r docker-down ||:
docker rmi r2r-r2r ||:
r2r serve --docker --config-path=r2r.toml --full --build ||:
