# Assuming you have not changed the general structure of the template no modification is needed in this file.
from typing import List

import adsk.core
import adsk.fusion

from . import commands, config, utils
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
        if not config.DEBUG:
            commands.start()
        else:
            commands.start()

        # Only for testing to execute the Board parsing

            progress = app.userInterface.createProgressDialog()
            progress.isCancelButtonShown = False
            progress.show("Converting S3DX file", "Load S3DX file", 0, 100, 0)
            # model: S3DModel = fromFile("C:/Users/Julian/plankton Kite/Kitefoilboards/Test2.s3dx", progress)
            # model: S3DModel = fromFile("C:/Users/Julian/plankton Kite/Kitefoilboards/TestBoard.s3dx", progress)
            model: S3DModel = S3DModel()
            settings = ConverterSettings()
            settings.closedStringer = False  # DONE
            settings.closedOutline = False  # DONE
            settings.closedSlices = True   # DONE
            settings.flipOutline = True  # DONE
            settings.mirrorSlices = False   # DONE
            settings.mirrorOutline = False  # DONE
            settings.fixedPoints = False    # DONE
            settings.fixedLines = False     # DONE
            config.debug_skip2d = False
            # settings.create3d = True

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

        # This will run the stop function in each of your commands as defined in commands/__init__.py
        if not config.DEBUG:
            commands.stop()

    except Exception as e:
        futil.handle_error('stop')
