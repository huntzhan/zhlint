#!/usr/bin/env bash
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
pip install -r "${PROJECT_DIR}/requirements.txt"
