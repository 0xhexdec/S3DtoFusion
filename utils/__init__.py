# missuse of the file to check if external imports are available and installing them on demand
import os
import subprocess
import sys
from typing import List

import adsk.core

from ..lib import fusion360utils as futil

app = adsk.core.Application.get()
try:
    import numpy

    futil.log("Numpy found", adsk.core.LogLevels.InfoLogLevel, True)
except ModuleNotFoundError:
    futil.log("Numpy not found, installing it now, this may take a while...", adsk.core.LogLevels.InfoLogLevel, True)
    if (sys.executable.find("Fusion360") != -1 and sys.executable.endswith("exe")):
        executable: str = sys.executable[:sys.executable.find("Fusion360")]
        executable += os.sep + "Python" + os.sep + "python.exe"

        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True, capture_output=True, shell=False)
        reqs = subprocess.run([executable, '-m', 'pip', 'install', 'numpy'], check=True, capture_output=True, shell=False, timeout=40)
        import numpy
        futil.log("Done", adsk.core.LogLevels.InfoLogLevel, True)
    elif (sys.executable.find("python") != -1):

        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True, capture_output=True, shell=False)
        reqs = subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy'], check=True, capture_output=True, shell=False, timeout=40)
        import numpy
        futil.log("Done", adsk.core.LogLevels.InfoLogLevel, True)
    else:
        directoryList: List[str] = sys.executable.split(os.sep)[:-1]
        directory: str = ""
        for element in directoryList:
            directory = directory + element + os.sep
        futil.log(">numpy< could not be installed automatically, this may happen if you are working on Mac. Try to manually install the python module for Fusion360's python version.\n" + 
                  "To do so, navigate to this directory: " + directory + "\n" + 
                  "Navigate to the >Python< directory in there \n" +
                  "Within a terminal, execute the Python application with the following parameters: \n" +
                  "-m pip install numpy\n" + "Rerun this Plugin.", adsk.core.LogLevels.ErrorLogLevel, True)

