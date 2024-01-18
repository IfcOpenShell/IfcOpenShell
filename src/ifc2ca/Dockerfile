# Use Miniconda base image
FROM continuumio/miniconda3:4.10.3

# Update Conda, install necessary libraries, and then install Mamba
RUN conda update -n base -c defaults conda && \
    conda install libarchive -c conda-forge -y && \
    conda install mamba -c conda-forge -y

# Install Code_Aster and Python dependencies with Conda
RUN mamba install -c conda-forge code-aster python=3.10 -y
