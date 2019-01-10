#!/bin/sh

rm -r __pycache__ text parses latmor_files gen 2> cleanup_log.txt
rm $2 *.pyc gen_errors.txt 2>> cleanup_log.txt
rm cleanup_log.txt