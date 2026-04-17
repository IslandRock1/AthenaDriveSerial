
To generate pybind stubs -> \
compile "SerialCommPython" target (Does not work with MinGW, needs Visual Studio, atleast in windows)

(preferably in venv) \
pip install pybind11-stubgen \
cd bindings/python \
py -m pybind11_stubgen SerialCommPython \
Then move files to examples/python