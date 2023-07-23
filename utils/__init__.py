# missuse of the file to check if external imports are available and installing them on demand
import subprocess
import sys

import adsk.core

app = adsk.core.Application.get()

try:
    import numpy

    # print("Numpy found, uninstalling it now")
    # reqs = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'numpy'],stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, timeout=40)
    # print("Done")
except ModuleNotFoundError:
    print("Numpy not found, installing it now")
    # reqs = subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy'], check=True, capture_output=True, shell=False, timeout=20)
    reqs = subprocess.call([sys.executable, '-m', 'pip', 'install', 'numpy'], shell=True, timeout=20)
    print("Done")
    import numpy
