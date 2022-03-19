#!/bin/bash
FILES=$(find . -name "*.py");
zimports --statsonly --expand-stars --keep-unused $FILES 2>&1 >/dev/null | grep -e "\[Writing\]" -e "\[Generating\]"
[[ "$?" = 1 ]];
