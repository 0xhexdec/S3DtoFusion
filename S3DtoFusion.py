# Assuming you have not changed the general structure of the template no modification is needed in this file.
import adsk.core

from . import commands, utils
from .fusionConverter.converter import Converter
from .fusionConverter.converterSettings import ConverterSettings
from .lib import fusion360utils as futil
from .s3dModel.s3dx import S3DModel, fromFile
from .s3dModel.types.enums import TangentType
from .utils import timer
from .utils.test import test

app = adsk.core.Application.get()

def run(context):
    try:
        # This will run the start function in each of your commands as defined in commands/__init__.py
        # commands.stop()
        # commands.start()

        # Only for testing to execute the Board parsing

        progress = app.userInterface.createProgressDialog()
        progress.isCancelButtonShown = False
        progress.show("Converting S3DX file", "Load S3DX file", 0, 100, 0)
        model: S3DModel = fromFile("C:/Users/Julian/plankton Kite/Kitefoilboards/Test2.s3dx", progress)
        # model: S3DModel = None
        settings = ConverterSettings()
        settings.closedStringer = False  # DONE
        settings.closedOutline = False  # DONE
        settings.closedSlices = True   # DONE
        settings.flipOutline = True  # DONE
        settings.mirrorSlices = False   # DONE
        settings.mirrorOutline = False  # DONE
        settings.fixedPoints = False    # DONE
        settings.fixedLines = False     # DONE
        settings.create3d = True


        settings.mergePoints = False    # seems to be needed by default. have i done this so far?
        settings.constrainedPoints = False
        converter = Converter(model, settings)
        converter.convertAll(app, None, progress)

        # test()

    except Exception as e:
        futil.handle_error('run')


def stop(context):
    try:
        # Remove all of the event handlers your app has created
        futil.clear_handlers()

        # This will run the start function in each of your commands as defined in commands/__init__.py
        # commands.stop()

    except Exception as e:
        futil.handle_error('stop')
