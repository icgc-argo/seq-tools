[![GitHub Actions CI Status](https://github.com/icgc-argo/seq-tools/workflows/CI%20tests/badge.svg)](https://github.com/icgc-argo/seq-tools/actions)

# Command line tools for sequencing data validations

## Installation

Follow these steps to install the `seq-tools`:
```
# clone the repo
git clone https://github.com/icgc-argo/seq-tools.git

# install using pip
cd seq-tools
pip install -r requirements.txt  # install Python dependencies
pip install .   # for development use: pip install -e .

# verify it by check the version
seq-tools -v
```

Try it with example submissions under `tests/submissions`
```
cd tests/submissions
seq-tools validate HCC1143N.WGS
```

## Testing

CI testing is enabled using GitHub Actions. To manually run tests:
```
pytest -v
```
