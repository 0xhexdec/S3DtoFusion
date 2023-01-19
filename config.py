# Application Global Variables
# This module serves as a way to share variables across different
# modules (global variables).

import os
from enum import Enum

from .fusionConverter.converterSettings import ConverterSettings


class SplineImplementationTechnique(Enum):
    TEXTCOMMANDS = "TextCommands"
    SURFACE_SPLIT = "Surface Split"
    PROJECT_TO_SURFACE = "Project to Surface (DEFAULT)"

# Flag that indicates to run in Debug mode or not. When running in Debug mode
# more information is written to the Text Command window. Generally, it's useful
# to set this to True while developing an add-in and set it to False when you
# are ready to distribute it.
DEBUG = False
debug_skip2d = False
is_settings_object_valid = False
is_Experimental_active = False

experimental_3d_spline_generation = False
experimental_3d_body_generation = False
experimental_3d_spline_implementation: SplineImplementationTechnique = SplineImplementationTechnique.PROJECT_TO_SURFACE

# Gets the name of the add-in from the name of the folder the py file is in.
# This is used when defining unique internal names for various UI elements
# that need a unique name. It's also recommended to use a company name as
# part of the ID to better ensure the ID is unique.
ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = 'PlanktonProgrammingPlatoon'

settings_object: ConverterSettings

# Palettes
sample_palette_id = f'{COMPANY_NAME}_{ADDIN_NAME}_palette_id'
