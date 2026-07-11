__doc__ = """Reverse 'Hook at Start' and 'Hook at End' of the rebar.
This tool doesn't work when you pick Shape Driven rebar and
'Include hooks in Rebar Shape definition' option is enabled."""

__title__ = "Reverse Hook"
__author__ = "Wolinski"
from Autodesk.Revit import DB
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

from pyrevit import script
from pyrevit import forms
from rebar_selector import RebarSelector

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView


def can_reverse(rebar):
    if rebar.IsRebarShapeDriven() and defines_hooks:
        return False
    elif rebar.IsRebarFreeForm:
        return True
    else:
        print("Unknown rebar type")


# Get reinforcement settings
settings = DB.Structure.ReinforcementSettings.GetReinforcementSettings(doc)
defines_hooks = settings.RebarShapeDefinesHooks

# Get selected object
rs = RebarSelector(doc, uidoc)
elements = rs.get_rebars()


# TODO: Make this flexible and working for single bars and rebar groups.
not_reversed_rebars = []
reversed_rebars = []

if not defines_hooks:
    # Handling transactions
    tg = DB.TransactionGroup(doc, "ReverseHook")
    tg.Start()
    for rebar in elements:
        if can_reverse(rebar):
            orient0 = rebar.GetHookOrientation(0)
            orient1 = rebar.GetHookOrientation(1)
            left = DB.Structure.RebarHookOrientation.Left
            right = DB.Structure.RebarHookOrientation.Right
            reversed_rebars.append(rebar.LookupParameter("Rebar Number").AsString())
            t = DB.Transaction(doc, "Reverse")
            t.Start()
            if orient0 == right:
                rebar.SetHookOrientation(0, left)
            elif orient0 == left:
                rebar.SetHookOrientation(0, right)
            if orient1 == right:
                rebar.SetHookOrientation(1, left)
            elif orient1 == left:
                rebar.SetHookOrientation(1, right)
            t.Commit()
        else:
            number = rebar.LookupParameter("Rebar Number").AsString()
            not_reversed_rebars.append(number)
    tg.Assimilate()
    if len(not_reversed_rebars) > 0:
        message = (
            "Operation failed!\n"
            + "Quantity of modified rebars: {}".format(len(reversed_rebars))
            + "\n"
            + "Rebar numbers not modified: {}".format(not_reversed_rebars)
        )
        forms.alert(msg=message, ok=True, exitscript=True)
else:
    message = "Operation failed! Reason: 'Include hooks in Rebar Shape definition' option is enabled."
    forms.alert(msg=message, ok=True, exitscript=True)
