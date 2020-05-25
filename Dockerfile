FROM continuumio/miniconda:4.7.12

ENV PATH=/opt/conda/condabin:$PATH

COPY . /tmp/seq-tools/

RUN cd /tmp/seq-tools/ && \
    conda env create -f environment.yml && \
    conda clean -a

ENV PATH=/opt/conda/envs/seq-tools-0.1.0/bin:$PATH

RUN groupadd -g 1000 ubuntu && \
    useradd -l -u 1000 -g ubuntu ubuntu -s /bin/bash && \
    install -d -m 0755 -o ubuntu -g ubuntu /home/ubuntu

USER ubuntu

CMD /bin/bash
