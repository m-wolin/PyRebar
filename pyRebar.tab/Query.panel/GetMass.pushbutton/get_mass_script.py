__doc__ = "Select all same number rebars based on selected rebar object."
__title__ = "GetMass"
__author__ = "MWolinski"
import Autodesk
from Autodesk.Revit import DB
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
from rebar_selector import RebarSelector
from rebar_cog import RebarCoG
from conversion import get_mass_unit
from pyrevit import script

ROUNDING = 2

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView


rs = RebarSelector(doc, uidoc)
rebar_collector = rs.get_rebars()

if not rebar_collector:
    print("No rebar selected. Please select at least one rebar element.")
    script.exit()

rebar_cog = RebarCoG(rebar_collector)

mass = rebar_cog.get_cog()[1]

mass_factor, mass_label = get_mass_unit(doc)

mass_text = "Total mass: " + str(round(mass * mass_factor, ROUNDING)) + " " + mass_label + "."

print(mass_text)
