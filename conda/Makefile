compile:
	conda activate conda-build && conda-build -c conda-forge . --keep-old-work --python 3.10.5

debug:
	conda activate conda-build && conda-debug -c conda-forge . --python 3.10.4

env:
	conda env update --f environment.yml --prune