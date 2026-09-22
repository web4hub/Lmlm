conda env create --name vbi python=3.10
conda activate vbi
# from pip: Recommended
pip install vbi
# from source: More recent update
git clone https://github.com/web4application/vbi.git
cd vbi
pip install .
# pip install -e .[all,dev,docs]

# To skip C++ compilation, use the following environment variable and install from source:
SKIP_CPP=1 pip install -e .
