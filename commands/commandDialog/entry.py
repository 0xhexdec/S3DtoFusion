
import os
from pydoc import doc
from sqlite3 import ProgrammingError
from xml.dom.minidom import parse, parseString

import adsk
import adsk.core
import adsk.fusion
from adsk.core import SelectionCommandInput
from adsk.fusion import ConstructionPlane
from pyexpat import ExpatError

from ... import config
from ...fusionConverter.converter import Converter
from ...fusionConverter.converterSettings import ConverterSettings
from ...lib import fusion360utils as futil
from ...s3dModel import s3dx
from ...s3dModel.s3dx import S3DModel
from ...utils import addin_settings

app = adsk.core.Application.get()
ui = app.userInterface



# TODO remove after tests
# skipFileSelection = True
skipFileSelection = False

CMD_ID = f'Plankton_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Import s3dx'
CMD_Description = 'Import a Shape3DX board to Fusion 360'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

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
    if panel:
        panel.deleteMe()
    panel = workspace.toolbarPanels.add(PANEL_ID, "S3DX import", "", False)


    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, "", False)

    # Specify if the command is promoted to the main toolbar.
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    futil.log(f'{CMD_NAME} stop')
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

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

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # Create a simple text box input.
    # inputs.addTextBoxCommandInput('text_box', 'Some Text', 'Enter some text.', 1, False)

    # Create a File selection popup button

    inputs.addBoolValueInput('fileButton', 'Select File', False, './resources/Folder', False)
    if skipFileSelection:
        inputs.addTextBoxCommandInput("filePathText", "", 'C:/Users/Julian/plankton Kite/Kitefoilboards/Nippy.s3dx', 3, True).tooltip = "Path to your S3DX file"
    else:
        inputs.addTextBoxCommandInput("filePathText", "", '<div style="color: #b5b5b5;"> (No File Selected) </div>', 3, True).tooltip = "Path to your S3DX file"

    # Create a plane selector
    selection = inputs.addSelectionInput("selectionButton", "Rocker Plane", "Select the plane you wish to act as the rocker. The view will be the same as in Shape3d X (tail left, nose right). If nothing is selected the ZY Plane will bve used so the names for the views match the board's view.")
    selection.addSelectionFilter("ConstructionPlanes")
    selection.setSelectionLimits(0, 1)
    selection.tooltip = "Select the Plane for the rocker, default is the XZ Plane"
    selection.tooltipDescription = "Select the plane for the Rocker, all other Lines will be added to different planes based and angled on the selected"
    selection.addSelection(adsk.fusion.Design.cast(app.activeProduct).rootComponent.xZConstructionPlane)
    selection.isVisible = False

    # create constrain group
    group = inputs.addGroupCommandInput("ConstrainSketchesGroup", "Constrain Sketches")
    group.tooltip = "Constain lines or points of the sketches"
    group.tooltipDescription = "CAUTION: Constraining takes some time. Even only fixing the Lines nearly doubles the execution time."
    group.isExpanded = True
    group.isEnabledCheckBoxDisplayed = False
    children = group.children

    input = children.addBoolValueInput("constrainPointsInput", "Constained Points", True, "", False)
    input.tooltip = "Constrains every Point with dimensions"
    input.tooltipDescription = "CAUTION: even though constraining all points in the Sketch makes Fusion happy, this is maybe not what you want. Constraining takes some time and makes the sketch cluttered. If you only want to prevent the sketch against unintentional point shifting, better use the >Fix Points< option."
    input.isVisible = False     # TODO currently deactivated
    input = children.addBoolValueInput("fixPointsInput", "Fix Points", True, "", False)
    input.tooltip = "Fixes all points in the sketch"
    input.tooltipDescription = "Applies the fix operation on all points so they are protected against unintentional moving."
    input = children.addBoolValueInput("fixLinesInput", "Fix Lines", True, "", False)
    input.tooltip = "Fixes all Lines in the sketch"
    input.tooltipDescription = "Applies the fix operation on all Lines so they are protected against unintentional moving. This might be more convenient as you have to unfix only one line segment instead of 4 Points (Per Spline/Bezier Segment)"
    input = children.addBoolValueInput("mergePointsInput", "Merge Points", True, "", False)
    input.tooltip = "Merges start and end points from the Splines"
    input.tooltipDescription = "Start and enpoints of the Splines are not connected when inserted. If you plan to manipulate these lines in Fusion, this option will bond these points together"
    input.isVisible = False     # TODO currently deactivated

    # TODO add option for "Merge Boxes into single sketch"

    group = inputs.addGroupCommandInput("2DGroup", "2D Options")
    group.isExpanded = False
    group.isEnabledCheckBoxDisplayed = False
    children = group.children

    input = children.addBoolValueInput("closeStringerInput", "Close Stringer", True, "", True)
    input.tooltip = "Connects the Rocker lines on Nose and Tail with a line"
    input.tooltipDescription = "By Connecting both rocker lines, the resulting shape is the Stringer."

    input = children.addBoolValueInput("closeOutlineInput", "Close Outline", True, "", True)
    input.tooltip = "Connects the Nose and Tail points with a new Centerline"
    input.tooltipDescription = "Adds a Centerline (that can be used a mirror line) and connects the Nose and Tail points with the center line. This shape can be used as a cut template. <br><i>Only applied to the Outline, not to aother top view lines.</i>"

    input = children.addBoolValueInput("closeSlicesInput", "Close Slices", True, "", True)
    input.tooltip = "Connects the first and last point of the Slice, essentially closing them at the Stringer"
    input.tooltipDescription = ""

    input = children.addBoolValueInput("flipOutlineInput", "Flip Outline", True, "", True)
    input.tooltip = "Flips the Outline and all top views to the right side, same as slices"
    input.tooltipDescription = "Shape3d makes the left sideof the Outline editable (Looking tail to Nose) but the right side of the Slices. This option flips the Outline and all other lines from top views to the right side."

    input = children.addBoolValueInput("mirrorSlicesInput", "Mirror Slices", True, "", False)
    input.tooltip = "Mirrors the Slices additionally to the left side."
    input.tooltipDescription = "By mirroring the Slice to the left side, the resulting shape is full-width slide instead of a half slice."

    input = children.addBoolValueInput("mirrorOutlineInput", "Mirror Outline", True, "", False)
    input.tooltip = "Mirrors the Outline additionally to the other side."
    input.tooltipDescription = "By mirroring the Outline to the other side, the resulting shape is full-width board template instead of a half sized. <br><i>Only applied to the Outline, not to other top view lines.</i>"

    if addin_settings.is_Experimental_active:
        group = inputs.addGroupCommandInput("3DGroup", "3D Options")
        group.isExpanded = False
        group.isEnabledCheckBoxDisplayed = True
        group.isEnabledCheckBoxChecked = False
        group.tooltip = "SLOW! UNFINISHED! Activate Lofted 3D Output"
        group.tooltipDescription = "<b>CAUTION:</b> SLOW Create a full board based on the shapes and lines imported from Shape3D. <br><br>This Feature is under Development. Fusion is very picky when it comes to lofting. If the Lofting fails, you will be notified and you can revert the Board import. Sadly, if it fails, your current board is not loftable by the current version of this Add-In. This is mostly due to sharp steps in the rockerline."
        children = group.children

        radioGroup = children.addRadioButtonGroupCommandInput("LoftTypeRadioButtonGroup", "Loft Type")
        radioGroup.tooltip = "Lofts the board as either a Solid or a Surface model"
        radioGroup.listItems.add("Solid", True, "", -1)
        radioGroup.listItems.add("Surface", False, "", -1)
        radioGroup.isEnabled = False

        radioGroup = children.addRadioButtonGroupCommandInput("BoxesRadioButtonGroup", "Boxes")
        radioGroup.tooltip = "Cuts the Boxes from the Board, just creates Bodies for the Boxes or both"
        radioGroup.listItems.add("Cut", False, "", -1)
        radioGroup.listItems.add("new Body", True, "", -1)
        radioGroup.listItems.add("Both", False, "", -1)
        radioGroup.isEnabled = False


    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # app.executeTextCommand('Commands.Start IntersectionCurve')
    # print("After intersection curve")
    inputs = args.command.commandInputs

    filename = adsk.core.TextBoxCommandInput.cast(inputs.itemById("filePathText")).text
    settings: ConverterSettings = ConverterSettings()
    settings.constrainedPoints = adsk.core.BoolValueCommandInput.cast(inputs.itemById("constrainPointsInput")).value
    settings.fixedLines = adsk.core.BoolValueCommandInput.cast(inputs.itemById("fixLinesInput")).value
    settings.fixedPoints = adsk.core.BoolValueCommandInput.cast(inputs.itemById("fixPointsInput")).value
    settings.mergePoints = adsk.core.BoolValueCommandInput.cast(inputs.itemById("mergePointsInput")).value

    settings.closedStringer = adsk.core.BoolValueCommandInput.cast(inputs.itemById("closeStringerInput")).value
    settings.closedOutline = adsk.core.BoolValueCommandInput.cast(inputs.itemById("closeOutlineInput")).value
    settings.closedSlices = adsk.core.BoolValueCommandInput.cast(inputs.itemById("closeSlicesInput")).value
    settings.flipOutline = adsk.core.BoolValueCommandInput.cast(inputs.itemById("flipOutlineInput")).value
    settings.mirrorSlices = adsk.core.BoolValueCommandInput.cast(inputs.itemById("mirrorSlicesInput")).value
    settings.mirrorOutline = adsk.core.BoolValueCommandInput.cast(inputs.itemById("mirrorOutlineInput")).value

    if addin_settings.is_Experimental_active:
        settings.create3d = adsk.core.GroupCommandInput.cast(inputs.itemById("3DGroup")).isEnabledCheckBoxChecked
        settings.loftAsSolid = adsk.core.RadioButtonGroupCommandInput.cast(inputs.itemById("LoftTypeRadioButtonGroup")).selectedItem.name == "Solid"
        name = adsk.core.RadioButtonGroupCommandInput.cast(inputs.itemById("BoxesRadioButtonGroup")).selectedItem.name
        settings.boxesCutFromBoard = name == "Cut" or name == "Both"
        settings.boxesAsBody = name == "new Body" or name == "Both"

    plane: adsk.fusion.ConstructionPlane = adsk.fusion.ConstructionPlane.cast(adsk.core.SelectionCommandInput.cast(inputs.itemById("selectionButton")).selection(0).entity)

    progress = ui.createProgressDialog()
    progress.isCancelButtonShown = False
    progress.show("Converting S3DX file", "Load S3DX file", 0, 100, 0)
    adsk.doEvents()
    model: S3DModel = s3dx.fromFile(filename, progress)
    converter = Converter(model, settings)
    progress.progressValue = 50
    progress.message = "Creating Sketches"
    adsk.doEvents()
    converter.convertAll(app, None, progress)
    # TODO change to using the selected rockerplane
    # converter.convertAll(app, plane, progress)
    progress.hide()
    futil.log(f'{CMD_NAME} Command Execute Event -> done')


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    futil.log(f'{CMD_NAME} Command Input Changed')
    changed_input = args.input
    inputs = args.inputs

    if changed_input.id == 'fileButton':
        # inputs = eventArgs.firingEvent.sender.commandInputs
        button = inputs.itemById('fileButton')
        button.isEnabled = False
        filename = getFilename()
        # TODO validate the file if enough curves are present
        if filename != "":
            adsk.core.TextBoxCommandInput.cast(inputs.itemById("filePathText")).formattedText = filename
        button.isEnabled = True

    # elif changed_input.id == 'selectionButton':
    #     selection: SelectionCommandInput = inputs.itemById("selectionButton")  # type: ignore
    #     if selection.selectionCount != 0:
    #         sel = selection.selection(0)
    #         plane: ConstructionPlane = sel.entity  # type: ignore
    #         futil.log(plane.name)

    # General logging for debug.
    # futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    # inputs.areInputsValid = False  # type: ignore
    filename = adsk.core.TextBoxCommandInput.cast(inputs.itemById("filePathText")).text
    selInput = adsk.core.SelectionCommandInput.cast(inputs.itemById("selectionButton"))
    if selInput.selectionCount > 0 and filename != "" and filename.find("(No File Selected)") == -1:
        sel = selInput.selection(0).entity
        if sel.classType() == adsk.fusion.ConstructionPlane.classType():
            args.areInputsValid = True
            return

    args.areInputsValid = False


# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')
    global local_handlers
    local_handlers = []


def getFilename() -> str:
    try:
        ui = app.userInterface
        if not skipFileSelection:
            dlg = ui.createFileDialog()
            dlg.title = 'Open S3DX File'
            dlg.filter = 'Shape3D File (*.s3dx)'
            if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
                return ""
            filename = dlg.filename
            futil.log(f"{filename}")
        else:
            filename = "C:/Users/Julian/plankton Kite/Kitefoilboards/Nippy.s3dx"

        return filename
    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        raise e
