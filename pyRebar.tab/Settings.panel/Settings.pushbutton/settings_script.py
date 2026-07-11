__doc__ = "Configure PyRebar settings: audit length thresholds and Select by Parameter defaults."
__title__ = "Settings"
__author__ = "MWolinski"

from pyrebar_settings import open_settings_dialog

doc = __revit__.ActiveUIDocument.Document

open_settings_dialog(doc)
