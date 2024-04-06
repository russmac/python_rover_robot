#!/usr/bin/env bash
rsync -avh --progress --exclude=venv --exclude=calibration * robot@robot:/robot
