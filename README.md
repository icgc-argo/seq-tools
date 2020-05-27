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

If you can run docker, no installation is needed. See the next section for how to run `seq-tools` using docker.

## Try it out
Try it with example submissions under `tests/submissions`
```
cd tests/submissions
seq-tools validate HCC1143N.WGS

# or validate all submission dirs using wildcard in one go
seq-tools validate *.*

# use docker to do the same
docker run -v `pwd`:`pwd` -w `pwd` quay.io/icgc-argo/seq-tools seq-tools validate *.*
```

## Testing

CI testing is enabled using GitHub Actions. To manually run tests:
```
pytest -v
```
