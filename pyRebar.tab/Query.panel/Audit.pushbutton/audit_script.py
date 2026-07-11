__doc__ = "Verify rebar elements in the model for common issues."
__title__ = "Audit rebars"
__author__ = "MWolinski"

from Autodesk.Revit import DB
from pyrevit import script
from rebar_selector import RebarSelector
from pyrebar_settings import get_setting
from conversion import get_length_unit

output = script.get_output()

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

FEET_TO_MM = 304.8
BBOX_TOLERANCE_FT = (
    0.003  # ~1 mm, used to round bounding box coordinates for duplicate matching
)
MIN_LENGTH_MM = get_setting("min_length_mm")
MAX_LENGTH_MM = get_setting(
    "max_length_mm"
)  # bars longer than this should typically be spliced


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
        eid = p.AsElementId()
        # ElementId.Value (Int64) replaces the deprecated ElementId.IntegerValue (Int32)
        # as of the Revit 2024 API; IntegerValue was removed entirely in later versions.
        id_value = eid.Value if hasattr(eid, "Value") else eid.IntegerValue
        return str(id_value)
    return None


def get_bar_number(rebar):
    """Return bar number as string."""
    return get_param_str(rebar, "Rebar Number")


def get_partition(rebar):
    """Return 'Partition' as string."""
    return get_param_str(rebar, "Partition")


def get_diameter_mm(rebar):
    """Return bar diameter in millimeters as float, or None if not available."""
    p = rebar.LookupParameter("Bar Diameter")
    if not p:
        return None
    try:
        return p.AsDouble() * FEET_TO_MM
    except:
        return None


def get_bar_count(rebar):
    """Return the number of physical bars this rebar element represents
    (existing positions in the set, excluding any suppressed positions)."""
    n_bars = rebar.NumberOfBarPositions
    return sum(1 for i in range(n_bars) if rebar.DoesBarExistAtPosition(i))


def format_basic_result(item):
    """Formats a (id, bar_no, partition) tuple for output."""
    return "ID: {0} | Bar Number: {1} | Partition: {2}".format(*item)


def format_long_bar_result(item):
    """Formats a (id, bar_no, partition, length_mm) tuple for output,
    converting the length to the document's Length display unit."""
    rebar_id, bar_no, partition, length_mm = item
    return "ID: {0} | Bar Number: {1} | Partition: {2} | Length: {3:.2f} {4}".format(
        rebar_id, bar_no, partition, length_mm * length_factor, length_label
    )


def get_duplicate_key(rebar):
    """Builds a signature used to detect rebars duplicated on top of each other
    (e.g. from accidental copy/paste or array). Returns None if a bounding box
    isn't available for the rebar.
    Signature: (host id, bar diameter, number of bar positions, rounded bbox)"""
    bbox = rebar.get_BoundingBox(None)
    if bbox is None:
        return None

    def round_pt(pt):
        r = BBOX_TOLERANCE_FT
        return (round(pt.X / r) * r, round(pt.Y / r) * r, round(pt.Z / r) * r)

    diam_param = rebar.LookupParameter("Bar Diameter")
    diam = round(diam_param.AsDouble(), 6) if diam_param else None
    host_id = rebar.GetHostId()
    n_bars = rebar.NumberOfBarPositions
    return (host_id, diam, n_bars, round_pt(bbox.Min), round_pt(bbox.Max))


# Collect rebars to test (all model rebars evaluate each against the ACTIVE view)
rs = RebarSelector(doc, uidoc)
rebar_list = list(rs.get_all_model_rebars())

short_bars = []  # (id, bar_no, partition)
long_bars = []  # (id, bar_no, partition, length_mm)
keep_straight_bars = []  # (id, bar_no, partition)
hidden_bars = []  # (id, bar_no, partition)
duplicate_key_map = {}  # signature -> list of (id, bar_no, partition)
diameter_stats = {}  # rounded diameter (mm) -> bar count
total_bar_count = 0

for r in rebar_list:
    bar_no = get_bar_number(r) or ""
    partition = get_partition(r) or ""
    info = (r.Id, bar_no, partition)

    length_mm = get_rebar_length_mm(r)
    workshop = get_param_str(r, "Workshop Instructions")
    shape = get_param_str(r, "Shape")

    bar_count = get_bar_count(r)
    total_bar_count += bar_count

    diam_mm = get_diameter_mm(r)
    if diam_mm is not None:
        diam_key = round(diam_mm, 6)
        diameter_stats[diam_key] = diameter_stats.get(diam_key, 0) + bar_count

    if length_mm is not None and length_mm < MIN_LENGTH_MM:
        short_bars.append(info)
    if length_mm is not None and length_mm > MAX_LENGTH_MM:
        long_bars.append(info + (length_mm,))
    if workshop == "Keep Straight" and shape not in ["00", "0", None]:
        keep_straight_bars.append(info)
    if r.IsHidden(view):
        hidden_bars.append(info)

    dup_key = get_duplicate_key(r)
    if dup_key is not None:
        duplicate_key_map.setdefault(dup_key, []).append(info)

duplicate_groups = [bars for bars in duplicate_key_map.values() if len(bars) > 1]


# OUTPUT
def print_check(title, results, formatter):
    output.print_md("### {0}".format(title))
    if not results:
        output.print_md("Not found.")
        return
    for item in results:
        output.print_md(formatter(item))


length_factor, length_label = get_length_unit(doc)

output.print_md("## Rebar Audit Results")
output.print_md(
    "Checked **{0}** rebar elements ({1} physical bars) against view '{2}'.".format(
        len(rebar_list), total_bar_count, view.Name
    )
)

output.print_md("### Statistics by Diameter")
if not diameter_stats:
    output.print_md("Not found.")
else:
    rows = ["| Diameter | Count |", "|---|---|"]
    for diam_key in sorted(diameter_stats):
        count = diameter_stats[diam_key]
        rows.append(
            "| {0:.2f} {1} | {2} |".format(
                diam_key * length_factor, length_label, count
            )
        )
    output.print_md("\n".join(rows))

print_check(
    "Too Short (< {0:.2f} {1})".format(MIN_LENGTH_MM * length_factor, length_label),
    short_bars,
    format_basic_result,
)

print_check(
    "Too Long (> {0:.2f} {1})".format(MAX_LENGTH_MM * length_factor, length_label),
    long_bars,
    format_long_bar_result,
)

print_check(
    "Keep Straight but Shape != 00",
    keep_straight_bars,
    format_basic_result,
)

print_check(
    "Hidden in view '{0}'".format(view.Name),
    hidden_bars,
    format_basic_result,
)

output.print_md("### Duplicated Bars")
if not duplicate_groups:
    output.print_md("Not found.")
else:
    for group in duplicate_groups:
        ids_str = ", ".join(str(item[0]) for item in group)
        bar_no = group[0][1]
        output.print_md(
            "Bar Number: {0} | {1} overlapping elements | IDs: {2}".format(
                bar_no, len(group), ids_str
            )
        )

output.print_md("---")
output.print_md("Done.")
