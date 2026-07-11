__doc__ = "Find and list rebars that are too short (<100mm), incorrect workshop instruction, or hidden in view."
__title__ = "Audit rebars"
__author__ = "MWolinski"

from Autodesk.Revit import DB
from pyrevit import script
from rebar_selector import RebarSelector

output = script.get_output()

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

FEET_TO_MM = 304.8


def get_rebar_length_mm(rebar):
    """Return total rebar length in millimeters as float, or None if not available."""
    p = rebar.LookupParameter("Length")
    if not p:
        return None
    try:
        return p.AsDouble() * FEET_TO_MM
    except:
        return None


def get_param_str(rebar, name):
    """Return parameter value as string, or None."""
    p = rebar.LookupParameter(name)
    if p is None:
        return None

    st = p.StorageType
    if st == DB.StorageType.String:
        return p.AsString()
    elif st == DB.StorageType.Integer:
        return str(p.AsInteger())
    elif st == DB.StorageType.Double:
        return str(p.AsDouble())
    elif st == DB.StorageType.ElementId:
        return str(p.AsElementId().IntegerValue)
    return None


def get_bar_number(rebar):
    """Return bar number as string."""
    return get_param_str(rebar, "Rebar Number")


def get_partition(rebar):
    """Return 'Partition' as string."""
    return get_param_str(rebar, "Partition")


# Collect rebars to test (all model rebars evaluate each against the ACTIVE view)
rs = RebarSelector(doc, uidoc)
rebar_collector = rs.get_all_model_rebars()

problematic = []  # (id, bar_no, partition, reasons_str)

for r in rebar_collector:
    length_mm = get_rebar_length_mm(r)
    workshop = get_param_str(r, "Workshop Instructions")
    shape = get_param_str(r, "Shape")

    cond_short = length_mm is not None and length_mm < 100.0  # < 10 cm
    cond_keep_straight = workshop == "Keep Straight" and shape not in ["00", "0", None]

    # Check if explicitly hidden in active view
    cond_hidden = r.IsHidden(view)

    reasons = []
    if cond_short:
        reasons.append("Too Short (< 100 mm)")
    if cond_keep_straight:
        reasons.append("Keep Straight but Shape != 00")
    if cond_hidden:
        reasons.append("Hidden in view '{0}'".format(view.Name))

    if reasons:
        bar_no = get_bar_number(r) or ""
        partition = get_partition(r) or ""
        reasons_str = "; ".join(reasons)
        problematic.append((r.Id, bar_no, partition, reasons_str))


# OUTPUT
count = len(problematic)
output.print_md("{0} - problematic rebars found{1}".format(count, ":" if count > 0 else "."))

if count > 0:
    for rid, bar_no, partition, reasons_str in problematic:
        output.print_md(
            "ID: {0} | Bar Number: {1} | Partition: {2} | Reason: {3}".format(rid, bar_no, partition, reasons_str)
        )

output.print_md("Done.")
