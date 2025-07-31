#!/bin/bash

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

REPO_NAME="$1"
if [ -z "$REPO_NAME" ]; then
  echo "Usage: $0 <repo-name>"
  exit 1
fi

AGTOOL="$HOME/agraph-install/bin/agtool"
CATALOG="root"
REPO_PATH="$HOME/agdb_tests/$REPO_NAME"

mkdir -p "$REPO_PATH"

$AGTOOL repos list | grep -q "$REPO_NAME"

if [ $? -eq 0 ]; then
  $AGTOOL repos delete "<$CATALOG:$REPO_NAME>"
fi

$AGTOOL repos create --supersede "<$CATALOG:$REPO_NAME>"

