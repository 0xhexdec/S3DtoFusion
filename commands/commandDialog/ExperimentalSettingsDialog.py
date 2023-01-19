
import os

import adsk
import adsk.core
import adsk.fusion

from ... import config
from ...lib import fusion360utils as futil
from ...s3dModel import s3dx

app = adsk.core.Application.get()
ui = app.userInterface



# TODO remove after tests
# skipFileSelection = True
skipFileSelection = False

CMD_ID = f'Plankton_{config.ADDIN_NAME}_set_experimental_dialog'
CMD_NAME = 'Experimental Settings'
CMD_Description = 'Manages experimental features of the S3DX import AddIn. Experimental features are not stable, may result in Fusion360 crashing and have other unexpected behaviour.'

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
old_state = False

# Executed when add-in is run.
def start():
    # Check if the old version is still running and close if needed
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def:
        cmd_def.deleteMe()

    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    # cmd_def.tooltip = "Activate Experimental AddIn Features"
    # cmd_def.

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
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # Create a simple text box input.
    # inputs.addTextBoxCommandInput('text_box', 'Some Text', 'Enter some text.', 1, False)

    # create constrain group
    group = inputs.addGroupCommandInput("FeaturesGroup", "Features")
    group.tooltip = "Activates and deactivates experimental features"
    group.tooltipDescription = "CAUTION: Experimental features are not stable, use with caution and expect errors and crashes!"
    group.isExpanded = True
    group.isEnabledCheckBoxDisplayed = False
    children = group.children

    input = children.addBoolValueInput("3dSplineGenerationInput", "3D Spline generation", True, "", config.experimental_3d_spline_generation)
    input.tooltip = "Creates the 3D Splines for compound lines"
    input.tooltipDescription = "CAUTION: Does take some time"
    input.isEnabled = not config.experimental_3d_body_generation
    input = children.addBoolValueInput("3dBodyGenerationInput", "3D Body generation", True, "", config.experimental_3d_body_generation)
    input.tooltip = "Lofts the Board based on the 3D Splines"
    input.tooltipDescription = "CAUTION: mostly fails"

        # create constrain group
    group2 = inputs.addGroupCommandInput("InnerWorkingsGroup", "Implementation")
    group2.tooltip = "Swaps implementations for features"
    group2.tooltipDescription = "CAUTION: Even though some of the listed features might be stable with the default implementation, changing to another implementation could lead to errors and crashes!"
    group2.isExpanded = True
    group2.isEnabledCheckBoxDisplayed = False
    children = group2.children

    input = children.addDropDownCommandInput("3dSplineGenerationTechniqueInput", "3D Spline Technique", adsk.core.DropDownStyles.LabeledIconDropDownStyle) # type: ignore
    dropdownItem = input.listItems
    for item in config.SplineImplementationTechnique:
        if config.experimental_3d_spline_implementation == item:
            dropdownItem.add(item.value, True, "", -1)
        else:
            dropdownItem.add(item.value, False, "", -1)
    input.tooltip = "Changes the implementation of the 3D Spline creation"
    input.tooltipDescription = "CAUTION: Only <Default> or <Stable> marked implementations are stable and not known to crash often."

    # futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)
    futil.add_handler(ui.commandTerminated, command_terminated)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    # futil.log(f'{CMD_NAME} Command Execute Event')
    pass

def command_preview(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Preview Event')

def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    global old_state

    if changed_input.id == '3dBodyGenerationInput':
        checkBox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('3dBodyGenerationInput'))
        splineCheckBox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('3dSplineGenerationInput'))
        # global old_state
        if checkBox.value:
            splineCheckBox.isEnabled = False
            old_state = splineCheckBox.value
            splineCheckBox.value = True
            config.experimental_3d_spline_generation = True
            config.experimental_3d_body_generation = True
        else:
            splineCheckBox.isEnabled = True
            splineCheckBox.value = old_state
            config.experimental_3d_spline_generation = old_state
            config.experimental_3d_body_generation = False
    elif changed_input.id == '3dSplineGenerationInput':
        old_state = adsk.core.BoolValueCommandInput.cast(inputs.itemById('3dSplineGenerationInput')).value
        config.experimental_3d_spline_generation = old_state
    elif changed_input.id == '3dSplineGenerationTechniqueInput':
        dropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById('3dSplineGenerationTechniqueInput'))
        config.experimental_3d_spline_implementation = config.SplineImplementationTechnique(dropdown.selectedItem.name)
        # futil.log(f'{config.experimental_3d_spline_implementation}')

def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    # futil.log(f'{CMD_NAME} Validate Input Event')
    pass

def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')
    global local_handlers
    local_handlers = []

def command_terminated(args: adsk.core.ApplicationCommandEventArgs):
    pass