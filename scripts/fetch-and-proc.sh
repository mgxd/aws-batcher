#!/bin/bash

# install and get a datalad data repository for fmriprep processing

set -eu

DATASET=$1
subj=$2

# single use test case
# $1 http://datasets-tests.datalad.org/abide2/RawData/
# $2 sub-29150

# index list of subjects by batch index
# subj=${subjs[${AWS_BATCH_JOB_ARRAY_INDEX}]}

# make data directory
mkdir data && pushd data

# first install the remote repository
datalad install -r $DATASET  # http://datasets-tests.datalad.org/abide2/RawData/${DATASET}

# now fetch only files necessary for fmriprep
datalad get -r -J 8 ./*/${subj}/{func,anat}/* ./*/${subj}/*/{func,anat}/* ./*/*.json

# return to project root
popd

# remove all symlinks - we may not need to do this since it's all in one container

#for fl in $(find -L . -type f -not -path "./data/*/.*" -regextype posix-egrep -regex ".*\.(json|tsv|gz)$"); do
#    # we have to be in the same directory as the files (relative symlinks)
#    pushd $(dirname $fl)
#    sed -i ';' $(basename $fl)
#    popd
#done
# and remove excess
#rm -rf data/*/.git data/*/.datalad data/*/.gitattributes


# ensure derivatives exists
if [ ! -d derivatives ]; then
    mkdir derivatives
fi

# make working directory
if [ ! -d scratch ]; then
    mkdir scratch
fi

datadir=$(ls $(pwd)/data/* -d)

cmd="fmriprep $datadir derivatives participant \
    --participant_label $subj \
    --nthreads 4 --mem_mb 8000 --output-space template \
    --template-resampling-grid 2mm --ignore slicetiming \
    -w scratch --fs-license-file /tmp/.fs_license.txt"

echo $cmd
eval $cmd

# and push results back to s3 bucket
