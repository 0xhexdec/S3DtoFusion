from .commandDialog import ExperimentalSettingsDialog
from .commandDialog import S3DToFusionDialog as commandDialog

commands = [
    commandDialog,
    ExperimentalSettingsDialog
    # paletteShow,
    # paletteSend
]


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    for command in commands:
        command.start()

# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()
