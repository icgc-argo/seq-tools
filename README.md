# Command line tools for sequencing data validations

## Installation

Follow these steps to install the `seq-tools`:
```
# clone the repo
git clone https://github.com/icgc-argo/seq-tools.git

# install using pip
cd seq-tools
pip install .   # for development use: pip install -e .

# verify it by check the version
seq-tools -v
```

Try it with example submission folders under `tests`
```
cd tests
seqtools validate HCC1143N.wgs
```
