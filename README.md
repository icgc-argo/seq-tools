[![GitHub Actions CI Status](https://github.com/icgc-argo/seq-tools/workflows/CI%20tests/badge.svg)](https://github.com/icgc-argo/seq-tools/actions)

# Command line tools for sequencing data validations

## Installation

For Ubuntu, please make sure you have Python 3 (tested on 3.7, other 3.x versions should work too) installed
first, then follow these steps to install the `seq-tools` (other OS should be similar):
```
# install samtools (which is mainly used to retrieve BAM header information)
sudo apt install samtools

# suggest to install jq to view JSON / JSONL in human-friendly format
sudo apt install jq

# clone the repo
git clone https://github.com/icgc-argo/seq-tools.git

# install using pip
cd seq-tools
pip3 install -r requirements.txt  # install Python dependencies
pip3 install .

# verify it by check the version
seq-tools -v
```

## Try it out using testing data

Try it with example submissions under `tests/submissions` (assume you already cloned the repository).
```
cd tests/submissions
# validate the metadata JSON under 'HCC1160T.valid' directory, assuming data files are in the same directory
seq-tools validate HCC1160T.valid/sequencing_experiment.json   # you should see summary of validation result

# to view details of the above validation, the 'jq' to is suggested to view prettified JSONL file
cat validation_report.PASS.jsonl | jq | less

# use '-d' option if data files are located in a different directory than where the metadata file lives
seq-tools validate -d ../seq-data/ metadata_file_only/HCC1143T.WGS.meta.json

# to view details of the above validation
cat validation_report.INVALID.jsonl | jq | less

# or validate all metadata JSONs using wildcard in one go, assuming all data files are under '../seq-data/'
seq-tools validate -d ../seq-data/ */*.json   # as the summary indicates, two validation reports are generated

# view reported issues for INVALID metadata
cat validation_report.INVALID.jsonl | jq | less

# view details for PASS metadata
cat validation_report.PASS.jsonl | jq | less
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
