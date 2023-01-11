
import os

import adsk
import adsk.core
import adsk.fusion

from ... import config
from ...lib import fusion360utils as futil
from ...s3dModel import s3dx
from ...utils import addin_settings

app = adsk.core.Application.get()
ui = app.userInterface



# TODO remove after tests
# skipFileSelection = True
skipFileSelection = False

CMD_ID = f'Plankton_{config.ADDIN_NAME}_set_experimental_dialog'
CMD_NAME = 'Activate Experimental'
CMD_Description = 'Activate Experimental Features'

# This is done by specifying the workspace, the tab, and the panel, and the
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'S3DXImportPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Executed when add-in is run.
def start():
    # Check if the old version is still running and close if needed
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def:
        cmd_def.deleteMe()

    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    # if panel:
    #     panel.deleteMe()
    # panel = workspace.toolbarPanels.add(PANEL_ID, "S3DX import", "", False)


    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, "", False)


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    if panel:
        command_control = panel.controls.itemById(CMD_ID)
        # Delete the button command control
        if command_control:
            command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()

    if panel:
        panel.deleteMe()

# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # Connect to the execute event.
    futil.add_handler(args.command.execute, command_execute)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    addin_settings.is_Experimental_active = not addin_settings.is_Experimental_active
    if addin_settings.is_Experimental_active:
        ui.commandDefinitions.itemById(CMD_ID).name = 'Deactivate Experimental'
    else:
        ui.commandDefinitions.itemById(CMD_ID).name = CMD_NAME
