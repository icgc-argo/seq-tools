#!/bin/bash

env=seq-tools-0.1.0

export PATH=/opt/conda/bin:$PATH

conda env create -f environment.yml
conda activate ${env}

echo 'export PATH=/opt/conda/bin:$PATH' >> ~/.bashrc
echo "conda activate ${env}" >> ~/.bashrc
