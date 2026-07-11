"""Shared persistent settings for PyRebar tools, backed by pyRevit's user config.

All PyRebar scripts that need a persisted setting should read/write through
this module (same config section name) so values are shared across tools.
"""
import os

from pyrevit import script
from pyrevit import forms
from pyrevit.forms import WPFWindow

SECTION_NAME = "PyRebarSettings"

DEFAULTS = {
    "min_length_mm": 100.0,
    "max_length_mm": 12000.0,
    "custom_parameters": ["Bar Diameter", "Partition", "Comments", "Schedule Mark"],
}

# The Settings dialog's xaml lives in the Settings.pushbutton bundle so it stays
# editable/visible next to the button that exposes it on the ribbon. Other
# scripts reach it through open_settings_dialog() below rather than duplicating
# the window, since script.get_bundle_file() only resolves within the bundle
# of the script currently being executed by pyRevit.
_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_XAML_PATH = os.path.join(
    _LIB_DIR, "..", "pyRebar.tab", "Query.panel", "Settings.pushbutton", "view.xaml"
)


def _config():
    return script.get_config(SECTION_NAME)


def get_setting(name):
    """Returns a persisted setting, falling back to its default if unset."""
    return _config().get_option(name, DEFAULTS.get(name))


def set_setting(name, value):
    """Stages a setting value for saving. Call save() afterwards to persist it."""
    _config().set_option(name, value)


def save():
    """Writes any pending setting changes to pyRevit's config file."""
    script.save_config()


class SettingsWindow(WPFWindow):
    """PyRebar settings dialog. Only writes to config when Save is clicked."""

    def __init__(self):
        WPFWindow.__init__(self, SETTINGS_XAML_PATH)
        self.txtMinLength.Text = str(get_setting("min_length_mm"))
        self.txtMaxLength.Text = str(get_setting("max_length_mm"))
        self.txtCustomParameters.Text = ", ".join(get_setting("custom_parameters"))
        self.saved = False

    def window_close(self, sender, args):
        """Closes the window without persisting anything."""
        self.Close()

    def save_settings(self, sender, args):
        """Validates and persists settings entered by the user."""
        try:
            min_length = float(self.txtMinLength.Text)
        except ValueError:
            forms.alert("Min bar length must be a number.", ok=True)
            return

        try:
            max_length = float(self.txtMaxLength.Text)
        except ValueError:
            forms.alert("Max bar length must be a number.", ok=True)
            return

        if min_length >= max_length:
            forms.alert("Min bar length must be smaller than max bar length.", ok=True)
            return

        custom_parameters = [p.strip() for p in self.txtCustomParameters.Text.split(",") if p.strip()]
        if not custom_parameters:
            forms.alert("Select by Parameter list cannot be empty.", ok=True)
            return

        set_setting("min_length_mm", min_length)
        set_setting("max_length_mm", max_length)
        set_setting("custom_parameters", custom_parameters)
        save()

        self.saved = True
        self.Close()


def open_settings_dialog():
    """Opens the PyRebar settings dialog modally.
    Returns:
        bool: True if the user saved changes, False if the dialog was cancelled/closed."""
    window = SettingsWindow()
    window.ShowDialog()
    return window.saved
