# FSSaveEditor
Cross platform python-based Save editor for [Flexible Survival](https://github.com/Nuku/Flexible-Survival)

Requires either `mise` or `uv` to install dependencies, build, and run

<details>
<summary>Supports the following exported save files (Versions from 2019 onwards)</summary>

```
FSBeastVariableSave.glkdata
FSCharacterVariableSave.glkdata
FSCharacterVariable2Save.glkdata
FSCharacterVariable3Save.glkdata
FSCharacterVariable4Save.glkdata
FSChildrenSave.glkdata
FSEventSave.glkdata
FSIndexedTextSave.glkdata
FSNewPlayerSave.glkdata
FSNumberListSave.glkdata
FSNumberSave.glkdata
FSPlayerListsSave.glkdata
FSPlayerSave.glkdata
FSPossessionSave.glkdata
FSRoomInventorySave.glkdata
FSRoomSave.glkdata
FSTextListSave.glkdata
FSTextSave.glkdata
FSTraitSave.glkdata
FSTruthSave.glkdata
FSUnbornChildSave.glkdata
FSVialDataSave.glkdata
SexStats.glkdata
```
</details>

## LICENSE

This project is available under the MIT license.  PySide6 is linked by the user at build time under the LGPLv3 license,
the full text of which can be found at https://www.gnu.org/licenses/lgpl-3.0.en.html or in the LICENSES directory of 
this repository.

## Usage

You need either `mise` or `uv` (with python >= 3.8) to run this project.

With mise:
```shell
mise run run
```

With uv:
```shell
uv run python FSSaveEditor.py
```

#### TODO:
 - Find examples of non-blank FSChildrenBunkerSave.glkdata, FSChildrenRoamingSave.glkdata, FSNoteSave.glkdata, and FSStorageSave.glkdata saves
