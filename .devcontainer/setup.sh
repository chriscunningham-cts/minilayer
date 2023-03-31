#!/usr/bin/env bash
set -x

sudo apt-get update && sudo apt-get -y install qemu binfmt-support qemu-user-static npm

sudo npm install -g @devcontainers/cli

pip install --user poetry

poetry install --with dev,generate

docker run --rm --privileged multiarch/qemu-user-static:latest --reset --credential yes -p yes
