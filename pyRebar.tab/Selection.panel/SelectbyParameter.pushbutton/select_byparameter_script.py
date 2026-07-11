__doc__ = "Select all rebars in view by chosen Parameter."
__title__ = "Select by Parameter"
__author__ = "Wolinski"
import re
from Autodesk.Revit import DB
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
from pyrevit import script
from pyrevit.forms import WPFWindow
from System.Collections.Generic import List
from rebar_selector import RebarSelector
from conversion import FEET_TO_MM
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView


xaml_file = script.get_bundle_file("view.xaml")

default_parameters = ["Bar Diameter", "Partition", "Comments", "Schedule Mark"]

# parameters_lst = List[String]()

# for parameter in default_parameters:
#     parameters_lst.Add(parameter)


rs = RebarSelector(doc, uidoc)
rebar_collector = rs.get_all_model_rebars()


def get_rebar_ids_by_parameter(rebar_collector, parameter_name, expected_value):
    """Finds ids of rebars matching given parameter values.
    Args:
    rebar_collector (DB.FilteredElementCollector)
    parameter_name (str): name of the parameter
    expected_value (str): value of the parameter
    Returns:
    List[DB.ElementId]"""
    rebar_ids = List[DB.ElementId]()

    for rebar in rebar_collector:
        param = rebar.LookupParameter(parameter_name)

        # Skip if parameter doesn't exist
        if param is None:
            continue

        # Get parameter value based on storage type
        param_value = None
        storage_type = param.StorageType

        if storage_type == DB.StorageType.String:
            param_value = param.AsString()
        elif storage_type == DB.StorageType.Double:
            param_value = str(
                param.AsDouble() * FEET_TO_MM
            )  # TODO: implement units sensitive code, based on project settings
        elif storage_type == DB.StorageType.Integer:
            param_value = str(param.AsInteger())
        elif storage_type == DB.StorageType.ElementId:
            param_value = str(param.AsElementId().IntegerValue)

        # Compare values
        if compare_values(param_value, expected_value):
            rebar_ids.Add(rebar.Id)
    return rebar_ids


def compare_values(param_value, expected_value):
    """Compare two values, handling numeric and string comparisons.
    Args:
        param_value (str): Parameter value from Revit
        expected_value (str): User input value
    Returns:
        bool: True if values match
    """
    # Check for None values first
    if param_value is None or expected_value is None:
        return False

    # Try numeric comparison first
    try:
        # Try to convert both to numbers
        param_num = string_to_number(param_value)
        expected_num = string_to_number(expected_value)

        # If both are numbers, compare numerically
        if param_num is not None and expected_num is not None:
            return param_num == expected_num
    except:
        pass

    # Fall back to string comparison (case-insensitive)
    return param_value.lower().strip() == expected_value.lower().strip()


def string_to_number(s):
    """Convert string to int or float, stripping units if present.
    To cover user input like '20' but also '20.0'.
    Args:
        s (str): String to convert
    Returns:
        int, float, or None: Converted number or None if not a number
    """
    if s is None:
        return None

    # Remove common units and whitespace
    s = s.strip()

    # Try to extract just the numeric part (handles "20mm", "20 mm", etc.)
    numeric_match = re.match(r"^([+-]?\d+\.?\d*)", s)
    if numeric_match:
        s = numeric_match.group(1)
    try:
        # Try to convert to number
        # Check if it's a float
        if "." in s:
            return float(s)
        else:
            # It's an integer
            num = int(s)
            return num
    except (ValueError, AttributeError):
        return None


class MainWindow(forms.WPFWindow):
    def __init__(self, xaml_file):
        WPFWindow.__init__(self, xaml_file)
        self.cmbBox.ItemsSource = default_parameters
        self.ShowDialog()

    def window_close(self, sender, args):
        """Closes opened xaml window."""
        self.Close()

    def select_rebar_by_parameter(self, sender, args):
        """Selects rebars with given parameters"""
        parameter_name = self.cmbBox.Text
        parameter_value = self.txtBoxValue.Text
        if parameter_name is None or len(parameter_name) < 1:
            forms.alert("Parameter name field cannot be empty", ok=True)
        if parameter_value is None:
            forms.alert("Parameter value field cannot be empty", ok=True)
        ids = get_rebar_ids_by_parameter(rebar_collector, parameter_name, parameter_value)
        uidoc.Selection.SetElementIds(ids)
        self.Close()

    def ComboBox_TextChanged(self, sender, args):
        return self.cmbBox.Text


window = MainWindow(xaml_file=xaml_file)
