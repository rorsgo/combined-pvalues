#!/bin/bash
#!/usr/bin/env python3

# doctests
python3 cpv/stouffer_liptak.py
python3 cpv/_common.py

##################################################################
python3 cpv/peaks.py --dist 50 --seed 0.02 data/close_peaks.bed > t

d=$(wc -l t | awk '{ print $1}')
test $d -ne 1 && echo "ERROR" $d

##################################################################
python3 cpv/peaks.py -c 4 --dist 1 --seed 0.02 data/close_peaks.bed > t

python3 cpv/pipeline.py
d=$(wc -l t | awk '{ print $1}')
test $d -ne 2 && echo "ERROR" $d

##########################################################################

for dist in 1 1000 10000000; do
    python3 cpv/peaks.py --dist $dist --seed 0.05 data/overlapping_peaks.bed > t
    d=$(wc -l t | awk '{ print $1}')
    test $d -ne 1 && echo "ERROR" $d
done

python3 cpv/comb-p hist -c 5 ./cpv/tests/data/pvals.bed > t

# unittests.
python3 cpv/tests/test.py

# the sum of the partials should add up the the final number in
# the non-partial
psum=$(python3 cpv/acf.py ./cpv/tests/data/pvals.bed -c 5 -d 1:500:50 \
    | awk '(NR > 1){ s += $4; }END{ print s}')
npsum=$(python3 cpv/acf.py ./cpv/tests/data/pvals.bed -c 5 -d 1:500:50 --full \
    | awk '(NR > 1){ s=$4 }END{ print s }')

test $psum -ne $npsum && echo "ERROR in ACF"

# test the acf output is as expected.
md=$(python3 cpv/acf.py -d 1:240:60 ./cpv/tests/data/pvals.bed -c 5 | md5sum \
    | awk '{ print $1 }')

md_expected=$(md5sum ./cpv/tests/data/expected_acf.txt | awk '{ print $1 }')

if [ $md != $md_expected ]; then
    echo "ACF OUTPUT different"
    echo $md
    echo $md_expected
fi

rm t
set -ex

python3 cpv/comb-p pipeline -c pvalue -p out --seed 0.05 --dist 1000 --region-filter-p 0.1 --region-filter-n 4 examples/file.bed

