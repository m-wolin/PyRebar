from Autodesk.Revit import DB

FEET_TO_MM = 304.8

# (UnitTypeId attribute name, factor to convert a millimeter value into this unit, label)
_LENGTH_SPECS = [
    ("Millimeters", 1.0, "mm"),
    ("Centimeters", 0.1, "cm"),
    ("Meters", 0.001, "m"),
    ("Inches", 1.0 / 25.4, "in"),
    ("FractionalInches", 1.0 / 25.4, "in"),
    ("Feet", 1.0 / FEET_TO_MM, "ft"),
    ("FeetFractionalInches", 1.0 / FEET_TO_MM, "ft"),
]

# (UnitTypeId attribute name, factor to convert a kilogram value into this unit, label)
_MASS_SPECS = [
    ("Kilograms", 1.0, "kg"),
    ("Tonnes", 0.001, "t"),
    ("PoundsMass", 2.2046226218, "lb"),
]

# (UnitTypeId attribute name, factor to convert a cubic-meter value into this unit, label)
_VOLUME_SPECS = [
    ("CubicMeters", 1.0, "m3"),
    ("CubicFeet", 35.3146667215, "ft3"),
    ("CubicYards", 1.30795062, "yd3"),
    ("CubicCentimeters", 1000000.0, "cm3"),
]


def _build_unit_map(specs):
    """Builds {UnitTypeId: (factor, label)}, skipping any name that doesn't
    exist as a DB.UnitTypeId attribute on this Revit API version."""
    unit_map = {}
    for name, factor, label in specs:
        unit_type_id = getattr(DB.UnitTypeId, name, None)
        if unit_type_id is not None:
            unit_map[unit_type_id] = (factor, label)
    return unit_map


LENGTH_UNITS = _build_unit_map(_LENGTH_SPECS)
MASS_UNITS = _build_unit_map(_MASS_SPECS)
VOLUME_UNITS = _build_unit_map(_VOLUME_SPECS)

DEFAULT_LENGTH_UNIT = (1.0, "mm")
DEFAULT_MASS_UNIT = (1.0, "kg")
DEFAULT_VOLUME_UNIT = (1.0, "m3")


def get_length_unit(doc):
    """Returns (factor, label) to convert a millimeter value into the document's
    Length display unit. Falls back to millimeters if the unit can't be read
    or isn't recognized."""
    try:
        unit_type_id = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
        return LENGTH_UNITS.get(unit_type_id, DEFAULT_LENGTH_UNIT)
    except Exception:
        return DEFAULT_LENGTH_UNIT


def get_mass_unit(doc):
    """Returns (factor, label) to convert a kilogram value into the document's
    Mass display unit. Falls back to kilograms if the unit can't be read or
    isn't recognized."""
    try:
        unit_type_id = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Mass).GetUnitTypeId()
        return MASS_UNITS.get(unit_type_id, DEFAULT_MASS_UNIT)
    except Exception:
        return DEFAULT_MASS_UNIT


def get_volume_unit(doc):
    """Returns (factor, label) to convert a cubic-meter value into the document's
    Volume display unit. Falls back to cubic meters if the unit can't be read or
    isn't recognized."""
    try:
        unit_type_id = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Volume).GetUnitTypeId()
        return VOLUME_UNITS.get(unit_type_id, DEFAULT_VOLUME_UNIT)
    except Exception:
        return DEFAULT_VOLUME_UNIT
