# missuse of the file to check if external imports are available and installing them on demand
import os
import subprocess
import sys
from typing import List

import adsk.core

from ..lib import fusion360utils as futil
from .. import config

app = adsk.core.Application.get()
ui = app.userInterface


def handleUnsuccessfulNumpyInstall(text: str):
    futil.log(text, adsk.core.LogLevels.ErrorLogLevel, True)
    ui.messageBox(text, config.ADDIN_NAME, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)

def installNumpy(pythonPath: str):
    try:
        subprocess.run([pythonPath, '-m', 'ensurepip', '--upgrade'], check=True, capture_output=True, shell=False, timeout=40)
        subprocess.run([pythonPath, '-m', 'pip', 'install', 'numpy'], check=True, capture_output=True, shell=False, timeout=40)
        import numpy
    except subprocess.CalledProcessError:
        handleUnsuccessfulNumpyInstall("The installation failed. Make sure you are connected to the internet as >pip< and >numpy< need to be downloaded.\nPlease rerun the Add-In and if the error persits, create an issue here: " + config.REPOSITORY_ISSUES_URL)
    except subprocess.TimeoutExpired:
        handleUnsuccessfulNumpyInstall("The installation failed due to a timeout. This may happen if your internet connection is slow.\nPlease rerun the Add-In and if the error persits, create an issue here: " + config.REPOSITORY_ISSUES_URL)
    except ModuleNotFoundError:
        handleUnsuccessfulNumpyInstall("Even though the installation was successful, the import failed.\nPlease rerun the Add-In and if the error persits, create an issue here: " + config.REPOSITORY_ISSUES_URL)

try:
    import numpy

    futil.log("Numpy imported", adsk.core.LogLevels.InfoLogLevel, True)
except ModuleNotFoundError:
    futil.log("Numpy not found, installing it now, this may take a while...", adsk.core.LogLevels.InfoLogLevel, True)
    futil.log(sys.executable,adsk.core.LogLevels.InfoLogLevel, True)
    if (sys.executable.find("Fusion360") != -1 and sys.executable.endswith("exe")):
        futil.log("Windows detected", adsk.core.LogLevels.InfoLogLevel, True)
        executable: str = sys.executable[:sys.executable.find("Fusion360")]
        executable += os.sep + "Python" + os.sep + "python.exe"
        installNumpy(executable)
    elif (sys.executable.find(".app") != -1):
        futil.log("Mac detected", adsk.core.LogLevels.InfoLogLevel, True)
        installNumpy(sys.executable)
    elif (sys.executable.find("python") != -1):
        futil.log("found python on path, just give it a try", adsk.core.LogLevels.InfoLogLevel, True)
        installNumpy(sys.executable)
    else:
        directoryList: List[str] = sys.executable.split(os.sep)[:-1]
        directory: str = ""
        for element in directoryList:
            directory = directory + element + os.sep
        msg: str = ">numpy< could not be installed automatically. Try to manually install the python module for Fusion360's python version.\n" + "To do so, navigate to this directory: " + directory + "\n" + "Navigate to the >Python< directory in there \n" + "Within a terminal, execute the Python application with the following parameters: \n" + "-m pip install numpy\n" + "Rerun this Plugin."  
        handleUnsuccessfulNumpyInstall(msg)
