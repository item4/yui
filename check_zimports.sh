#!/bin/bash
FILES=$(find . -name "*.py" -not -path "*/templates*");
zimports --statsonly --expand-stars --keep-unused $FILES 2>&1 >/dev/null | grep -e "\[Writing\]" -e "\[Generating\]"
[[ "$?" = 1 ]];
