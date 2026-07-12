# PyRebar
[PyRevit](https://github.com/pyrevitlabs/pyRevit/tree/master) extension for Autodesk Revit :registered: reinforcement modelling.
This is a toolkit of scripts that speeds up common, repetitive tasks in reinforcement detailing: checking a model for mistakes, selecting bars by criteria, and calculating quantities.

<img width="851" height="94" alt="image" src="https://github.com/user-attachments/assets/139c3379-cda9-4473-9d6c-e2fd01265b08" />

✅ Currently tested with **Autodesk Revit 2027**, should work with earlier versions as well.

**Any improvement ideas and features to add are welcome!**

## Installation
Watch the video:
<p align="center">
  <a href="https://youtu.be/H4hwBS1FI6M">
    <img src="https://img.youtube.com/vi/H4hwBS1FI6M/maxresdefault.jpg" alt="PyRebar Installation Video" width="600">
  </a>
</p>

## How selection works

Tools differ in how they pick up rebar to work with - worth knowing before you click a button:

- **Selection required** (*Same Number*, *Reverse hook*, *RebarCoG*, *Get mass*): acts on whatever rebar you have selected. If nothing is selected, you'll be prompted to pick elements in the model.
- **Selection optional, falls back to view** (*Select Rebar Type*, *Obscure/Unobscure bars*): acts on your selection if you have one, otherwise on every rebar visible in the active view.
- **Always whole model** (*Audit rebars*, *Select by Parameter*): ignores any current selection and always scans every rebar in the project.

## ✨Features

### 👁️ View tab
- **Unobscure bars** - Turns off "obscured" display for reinforcement bars, making hidden-line bars visible again.
- **Obscure bars** - Marks reinforcement bars as obscured (hidden behind other elements) in the current view.

### ⬇️ Selection tab
- **Same Number** - Given one selected rebar, selects every other rebar sharing the same "Rebar Number" *and* "Partition" - handy for isolating a whole bar mark to check or edit it together.
- **Select by Parameter** - Opens a dialog where you type (or pick from a saved list) a parameter name and value; selects every rebar in the model whose parameter matches. The dropdown of parameter names is configurable from the Settings tool.
- **Select Rebar Type** - Opens a dialog listing every rebar type used in the model; selects all rebars of the type you pick.

### 🛠️ Modify tab
- **Reverse hook** - Swaps the Left/Right orientation of the "Hook at Start" and "Hook at End" on the selected rebar(s). :warning: Only works when **'Include hooks in Rebar Shape definition'** is *disabled* in Revit's Reinforcement Settings - if it's enabled, the tool will report failure and change nothing.

### 🔍 Query tab
- **Audit rebars** - Scans the whole model and reports, against the active view:
  - Bars shorter than the minimum length, or longer than the maximum length (both configurable in Settings; 100 mm / 12000 mm by default - bars over the maximum typically need a splice).
  - Bars marked with the "Keep Straight" workshop instruction whose Shape parameter isn't actually straight.
  - Bars hidden in the active view.
  - Bars duplicated on top of each other (e.g. from an accidental copy/paste), grouped by overlapping bounding box.
  - A **Statistics by Diameter** table: how many physical bars exist for each bar diameter in the model.
- **RebarCoG** - Calculates the mass-weighted centre of gravity of the selected rebar(s), relative to the project base point, along with their total mass (both shown in project units). Optionally places a small sphere generic model at the calculated point so you can see it in the model.
- **Rebar ratio** - Calculates the reinforcement-to-concrete ratio (rebar mass ÷ concrete volume) for one or more structural elements that can host rebar (e.g. a wall or column). Acts on your current selection, or prompts you to pick elements if nothing is selected; if you select rebar instead of (or along with) its host, the tool resolves it to the host element automatically. All rebar hosted by the selected element(s) is included; if several elements are selected, their masses and volumes are summed before the ratio is computed.
- **Get mass** - Calculates the total mass of the selected rebar element(s) from $\frac{\pi d^2}{4} L_{bar}$ (where $d$ is bar diameter and $L_{bar}$ is the bar length Revit reports), summed across all bars and printed in project mass units.

### ⚙️ Settings tab
- **Settings** - Configure the minimum/maximum length thresholds used by *Audit rebars*, and edit the list of parameter names offered by *Select by Parameter*.

## 📄 License

[GPL-3.0](LICENSE.txt), matching pyRevit's own license - as a pyRevit extension, PyRebar is a derivative work, so it must be released under the same license.

I do not work in Revit that often anymore but will try to maintain this add-in for future versions.

