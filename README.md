[![GitHub Actions CI Status](https://github.com/icgc-argo/seq-tools/workflows/CI%20tests/badge.svg)](https://github.com/icgc-argo/seq-tools/actions)

# Command line tools for sequencing data validations

## Installation

Follow these steps to install the `seq-tools`:
```
# install samtools (if you don't use docker)
sudo apt install samtools

# clone the repo
git clone https://github.com/icgc-argo/seq-tools.git

# install using pip
cd seq-tools
pip install -r requirements.txt  # install Python dependencies
pip install .   # for development use: pip install -e .

# install a particular release without cloning the repo
pip install git+https://github.com/icgc-argo/seq-tools.git@0.5.0

# verify it by check the version
seq-tools -v
```
If you can run docker, no installation is needed. See the next section for how to run `seq-tools` using docker.

## Try it out using testing data

Try it with example submissions under `tests/submissions` (assume you cloned the repository).
```
cd tests/submissions
seq-tools validate HCC1143N.WGS

# or validate all submission dirs using wildcard in one go
seq-tools validate *.*

# use docker to do the same
docker run -v `pwd`:`pwd` -w `pwd` quay.io/icgc-argo/seq-tools:0.5.0 seq-tools validate *.*

# validate metadata only
seq-tools validate -m "`cat HCC1160T.valid/sequencing_experiment.json`"

docker run quay.io/icgc-argo/seq-tools:0.5.0 seq-tools validate -m "`cat HCC1160T.valid/sequencing_experiment.json`"
```

## Use it to validate your own submission

Submission of sequencing data is organized in submission directories, each directory includes
a JSON file named `sequencing_experiment.json` and all sequencing files generated from the experiment.

`sequencing_experiment.json` contains required metadata describing a sequencing experiment, read groups, and
the sample for which the experiment was performed. Please check out more detailed instruction how to prepare this
file at [here](https://docs.icgc-argo.org/docs/submission/submitting-molecular-data#understanding-the-song-metadata-fields).

Sequencing files can be in BAM or FASTQ format.

To validate a submission, simply run (replace <submission_dir> with your actual directory):
```
seq-tools validate <submission_dir> [submission_dir_2 ...]
```

Note that you can invoke a validation for multiple submission directories.

Brief information including overall validation result will be displayed in the console, itemized report is
available in a JSON file named `report.json` under each submission directory. Please fix reported issues and
run the validation again until result of every check is PASS.


## Testing

CI testing is enabled using GitHub Actions. To manually run tests:
```
pytest -v
```
