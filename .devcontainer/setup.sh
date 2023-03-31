#!/usr/bin/env bash
set -x

npm install -g @devcontainers/cli

pip install poetry

poetry install --with dev,generate

apt-get -y install qemu binfmt-support qemu-user-static

docker run --rm --privileged multiarch/qemu-user-static:latest --reset --credential yes -p yes
