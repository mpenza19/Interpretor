    #!/bin/sh

# Usage:
# bash scanlat.sh input_text_file is_macronized_input
#
# where input_text_file is in the subdirectory ../input

bash clean_dir.sh

echo $1
echo $2

time python2 parse_eng.py < $1
time python2 transfer_eng2lat.py
time python2 generate.py 2> gen_errors.txt
cat gen/* > $2
cat gen_errors.txt
open $2