#!/bin/sh

# Usage:
# bash scanlat.sh input_text_file is_macronized_input
#
# where input_text_file is in the subdirectory ../input

rm -r __pycache__ text parses latmor_files gen 2> cleanup_log.txt
mkdir text parses parses/source parses/target latmor_files gen 2>> cleanup_log.txt
rm $2 *.pyc gen_errors.txt 2>> cleanup_log.txt
rm cleanup_log.txt

echo $1
echo $2

time python2 parse_eng.py < $1
time python2 transfer_eng2lat.py
time python2 generate.py 2> gen_errors.txt
cat gen/* > $2
open $2