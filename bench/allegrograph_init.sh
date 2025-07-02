#!/bin/bash

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

REPO_NAME="benchmark"
AGTOOL="$HOME/agraph-install/bin/agtool"
CATALOG="root"
REPO_PATH="/home/mairacs/agdb/$REPO_NAME"


mkdir -p "$REPO_PATH"

$AGTOOL repos list | grep -q "$REPO_NAME"

if [ $? -eq 0 ]; then
    $AGTOOL repos delete "<$CATALOG:$REPO_NAME>"
fi

$AGTOOL repos create --supersede "<$CATALOG:$REPO_NAME>" 'REPO_PATH';
