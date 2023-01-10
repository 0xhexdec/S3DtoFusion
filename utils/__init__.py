# missuse of the file to check if external imports are available
import subprocess
import sys

import adsk.core

app = adsk.core.Application.get()
try:
    import numpy
except ModuleNotFoundError:
    print("Numpy not found, installing it now")
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'install', 'numpy'])
