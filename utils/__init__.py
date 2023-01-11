# missuse of the file to check if external imports are available and installing them on demand
import subprocess
import sys

import adsk.core

app = adsk.core.Application.get()

try:
    import numpy
except ModuleNotFoundError:
    print("Numpy not found, installing it now")
    reqs = subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy'], check=True, capture_output=True, shell=False)
    import numpy
