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

# to install a specific version (eg, 1.1.0) without cloning the git repository
pip install git+https://github.com/icgc-argo/seq-tools.git@1.1.0  # replace 1.1.0 to other released version as needed

# to uninstall
pip uninstall seq-tools

# verify it by check the version
seq-tools -v
```

If you can run docker and prefer to use it, then there is no need to install `seq-tools` beforehand.
See one of the examples below how to use `seq-tools` in docker container.

## Try it out using testing data

Try it with example submissions under `tests/submissions` (assume you already cloned the repository).
```
cd tests/submissions
# validate the metadata JSON under 'HCC1160T.valid' directory, assuming data files are in the same directory
seq-tools validate HCC1160T.valid/sequencing_experiment.json   # you should see summary of validation result

# to view details of the above validation result
cat validation_report.PASS.jsonl | jq . | less

# use '-d' option if data files are located in a different directory than where the metadata file lives
seq-tools validate -d ../seq-data/ metadata_file_only/HCC1143T.WGS.meta.json

# to view details of the above validation result
cat validation_report.INVALID.jsonl | jq . | less

# or validate all metadata JSONs using wildcard in one go, assuming all data files are under '../seq-data/'
seq-tools validate -d ../seq-data/ */*.json   # as the summary indicates, three validation reports are generated

# view reported issues for INVALID metadata files
cat validation_report.INVALID.jsonl | jq . | less

# view details for PASS-with-WARNING metadata files
cat validation_report.PASS-with-WARNING.jsonl | jq . | less

# view details for PASS metadata files
cat validation_report.PASS.jsonl | jq . | less

# if you can run docker, here is how you may use it. Not suggested for users unfamiliar with Docker
cd ..  # make sure you are under the `tests` directory
docker pull quay.io/icgc-argo/seq-tools:1.0.1
alias seq-tools-in-docker="docker run -t -v `pwd`:`pwd` -w `pwd` quay.io/icgc-argo/seq-tools:1.0.1 seq-tools"
seq-tools-in-docker validate -d seq-data/ submissions/*/*.json  # you should see the same results as running seq-tools without docker
```

## Use it to validate your own submissions

Similar to the example submissions under the `tests/submissions`, you have two options
to organize your own submissions:
1. either putting each metadata JSON file and its related data files in its own folder,
such as `tests/submissions/HCC1160T.valid/sequencing_experiment.json` and `test_rg_6.bam` are under
`HCC1160T.valid` folder with no other submissions in it;

2. or putting different metadata files together into one folder but all related data files separately
elsewhere, such as `tests/submissions/metadata_file_only` contains two metadata files:
`HCC1143N.WGS.meta.json` and `HCC1143T.WGS.meta.json`, data files related to them are under `tests/seq-data`

For the first option, you can launch validation by specifying the metadata file, for example: `seq-tools validate tests/submissions/HCC1160T.valid/sequencing_experiment.json`. Note in this case there is no need to provide
`-d` parameter since the data file is located under the same folder as the metadata file.
For the second option, it's necessary to use `-d` to specify the directory where data files are located, for example, `seq-tools validate -d tests/seq-data tests/submissions/metadata_file_only/*.json`

## Testing

Continuous integration testing is enabled using GitHub Actions. For validation check developers, you can manually run tests by:
```
pytest -v
```
