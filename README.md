[![GitHub Actions CI Status](https://github.com/icgc-argo/seq-tools/workflows/CI%20tests/badge.svg)](https://github.com/icgc-argo/seq-tools/actions)

# Command line tools for sequencing data validations

## Installation

For Ubuntu, please follow these steps to install the `seq-tools` (other OS should be similar):
```
# install samtools (which is mainly used to retrieve BAM header information)
sudo apt install samtools

# clone the repo
git clone https://github.com/icgc-argo/seq-tools.git

# install using pip
cd seq-tools
pip install -r requirements.txt  # install Python dependencies
pip install .

# verify it by check the version
seq-tools -v
```

## Try it out using testing data

Try it with example submissions under `tests/submissions` (assume you already cloned the repository).
```
cd tests/submissions
# validate the submission under 'HCC1160T.valid' directory
seq-tools validate HCC1160T.valid   # you should see summary of validation result

# or validate all submission dirs using wildcard in one go
seq-tools validate *.*   # you should see summary of validation result
```

## Use it to validate your own submission

Submission of sequencing data is organized in submission directories, each directory includes
a JSON file named `sequencing_experiment.json` and all sequencing files generated from the experiment and you plan to submit.

`sequencing_experiment.json` contains required metadata describing a sequencing experiment, read groups, and
the sample for which the experiment was performed. Please check out more detailed instruction how to prepare this
file at [here](https://docs.icgc-argo.org/docs/submission/submitting-molecular-data#understanding-the-song-metadata-fields).

Sequencing files can be in BAM or FASTQ format.

To validate a submission, simply run (replace <submission_dir> with your actual directory):
```
seq-tools validate <submission_dir> [submission_dir_2 ...]
```

Note that you can invoke a validation for multiple submission directories.

Brief information including overall validation result will be displayed in the console, itemized report with
more details is available in a JSON file named `report.json` under each submission directory. Please fix
reported issues and run the validation again until result of every check is PASS.


## Testing

Continuous integration testing is enabled using GitHub Actions. For validation check developers, you can manually run tests by:
```
pytest -v
```
