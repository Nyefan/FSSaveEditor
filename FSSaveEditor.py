import sys
import json
import re
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit,
    QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QVBoxLayout,
    QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QIntValidator, QPalette, QColor
import darkdetect

with open("config.json", "r") as f:
    config = json.load(f)

try:
    with open("lang.json", "r") as f:
        lang = json.load(f)
except FileNotFoundError:
    lang = {}


def apply_theme(app):
    app.setStyle("Fusion")
    if darkdetect.isDark():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))
        app.setPalette(palette)


class SaveEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flexible Survival Save Editor")
        self.setWindowIcon(QIcon("favicon.ico"))
        self.resize(780, 805)
        self.setFixedHeight(805)

        self.characters = []
        self.header_lines = []
        self.current_character_index = 0
        self.value_names = []
        self.value_types = {}
        self.first_name_key = None
        self.bool_string_values = {}
        self.line_by_line = False
        self.is_encoded = False
        self.value_entries = {}

        main_layout = QVBoxLayout(self)

        self.editor_widget = QWidget()
        self.editor_layout = QGridLayout(self.editor_widget)
        self.editor_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.editor_widget, stretch=1)

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 10, 5, 10)

        self.dropdown_widget = QWidget()
        self.dropdown_layout = QHBoxLayout(self.dropdown_widget)
        self.dropdown_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.dropdown_widget)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_save)
        button_layout.addWidget(self.load_button)

        self.current_file_label = QLabel("No file loaded")
        button_layout.addWidget(self.current_file_label)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete Line")
        self.delete_button.clicked.connect(self.delete_current_line)
        self.delete_button.hide()
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()
        main_layout.addWidget(button_widget)

    def load_save(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Save File", "", "Encoded/Decoded Save File (*.glkdata)"
        )
        if not file_path:
            return
        self.current_file_label.setText(os.path.basename(file_path))
        config_key = os.path.basename(file_path).replace(".glkdata", "")
        if config_key not in config:
            QMessageBox.critical(
                self, "Error",
                f"No configuration found for '{config_key}' in config.json.\n"
                "Please contact Meus Artis if you are trying to load a supported file that isn't blank."
            )
            return
        self.line_by_line = False
        if isinstance(config[config_key], list) and len(config[config_key]) > 0 and config[config_key][0].get("flag") == "LineByLine":
            self.line_by_line = True
            self.value_names = [entry["name"] for entry in config[config_key][1:]]
            self.value_types = {entry["name"]: entry["type"] for entry in config[config_key][1:]}
        else:
            self.value_names = [entry["name"] for entry in config[config_key]]
            self.value_types = {entry["name"]: entry["type"] for entry in config[config_key]}
        self.first_name_key = self.value_names[0] if not self.line_by_line else None
        self.bool_string_values = {entry["name"]: entry["values"] for entry in config.get("BoolString", [])}
        with open(file_path, "r") as f:
            lines = f.readlines()
            self.header_lines = lines[:2]
            raw_lines = [line.strip() for line in lines[2:]]
            self.is_encoded = all(line.startswith("S") for line in raw_lines if line)
            self.characters = [self.decode_glkdata_line(line) for line in raw_lines] if self.is_encoded else raw_lines
        if self.characters:
            if self.line_by_line:
                names = [f"Line {i+1}" for i in range(len(self.characters))]
                self.create_dropdown(names)
                self.current_character_index = 0
                self.delete_button.show()
            else:
                names = [self.parse_line(line).get(self.first_name_key, "Unknown") for line in self.characters]
                self.create_dropdown(names)
                self.current_character_index = names.index("yourself") if "yourself" in names else 0
                self.delete_button.hide()
            self.dropdown.blockSignals(True)
            self.dropdown.setCurrentIndex(self.current_character_index)
            self.dropdown.blockSignals(False)
            self.display_character()

    def create_dropdown(self, names):
        while self.dropdown_layout.count():
            item = self.dropdown_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not self.line_by_line:
            self.dropdown_layout.addWidget(QLabel(lang.get(self.first_name_key, self.first_name_key)))
        self.dropdown = QComboBox()
        self.dropdown.setFixedWidth(100)
        self.dropdown.addItems(names)
        self.dropdown.currentIndexChanged.connect(self.on_dropdown_select)
        self.dropdown_layout.addWidget(self.dropdown)

    def on_dropdown_select(self, index):
        self.current_character_index = index
        self.display_character()

    def parse_line(self, line):
        parts = [m[0] or m[1] for m in re.findall(r'"(.*?)";|([^ ]+)', line)]
        parsed_data = {}
        for i in range(min(len(self.value_names), len(parts))):
            name = self.value_names[i]
            value = parts[i]
            if self.value_types[name] == "Integer":
                try:
                    parsed_data[name] = int(value)
                except ValueError:
                    parsed_data[name] = 0
            elif self.value_types[name] == "Bool":
                parsed_data[name] = bool(int(value)) if value.isdigit() else False
            else:
                parsed_data[name] = value
        return parsed_data

    def delete_current_line(self):
        if not self.characters or len(self.characters) <= 1:
            QMessageBox.warning(self, "Delete Line", "Cannot delete the last line without crashing")
            return
        if QMessageBox.question(self, "Delete Line", f"Are you sure you want to delete Line {self.current_character_index + 1}?") != QMessageBox.StandardButton.Yes:
            return
        del self.characters[self.current_character_index]
        names = [f"Line {i+1}" for i in range(len(self.characters))]
        self.dropdown.blockSignals(True)
        self.dropdown.clear()
        self.dropdown.addItems(names)
        if self.current_character_index >= len(self.characters):
            self.current_character_index = len(self.characters) - 1
        self.dropdown.setCurrentIndex(self.current_character_index)
        self.dropdown.blockSignals(False)
        self.display_character()

    def display_character(self):
        while self.editor_layout.count():
            item = self.editor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not self.characters:
            return
        self.value_entries = {}
        character_data = self.parse_line(self.characters[self.current_character_index])
        for idx, name in enumerate(self.value_names):
            row, col = idx // 3, idx % 3
            display_name = lang.get(name, name)
            label = QLabel(display_name)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.editor_layout.addWidget(label, row, col * 2)
            if not self.line_by_line and name == self.first_name_key:
                entry = QLineEdit(str(character_data.get(name, "")))
                entry.setReadOnly(True)
                entry.setFixedWidth(110)
            elif self.value_types[name] in ("Bool", "BoolString"):
                entry = QCheckBox()
                if self.value_types[name] == "Bool":
                    entry.setChecked(bool(character_data.get(name, False)))
                else:
                    entry.setChecked(character_data.get(name) == self.bool_string_values[name][1])
            elif self.value_types[name] == "Integer":
                entry = QLineEdit(str(character_data.get(name, 0)))
                entry.setFixedWidth(60)
                entry.setValidator(QIntValidator())
            else:
                entry = QLineEdit(str(character_data.get(name, "")))
                entry.setFixedWidth(110)
            self.editor_layout.addWidget(entry, row, col * 2 + 1)
            self.value_entries[name] = entry

    def decode_glkdata_line(self, line):
        output = ""
        i = 0
        while i < len(line):
            if line[i] == 'S':
                i += 1
                ascii_codes = ""
                while i < len(line) and line[i] != ';':
                    ascii_codes += line[i]
                    i += 1
                i += 1
                codes = ascii_codes.split(',')
                if codes == ['0']:
                    output += '""; '
                else:
                    if codes and codes[-1] == '0':
                        codes = codes[:-1]
                    decoded = ''.join(chr(int(c)) for c in codes if c.isdigit())
                    output += f'"{decoded}"; '
            else:
                start = i
                while i < len(line) and not line[i].isspace():
                    i += 1
                output += line[start:i] + " "
                while i < len(line) and line[i].isspace():
                    i += 1
        return output.strip()

    def encode_glkdata_line(self, line):
        output = []
        i = 0
        while i < len(line):
            if line[i] == '"':
                i += 1
                start = i
                while i < len(line) and line[i] != '"':
                    i += 1
                text = line[start:i]
                i += 1
                if i < len(line) and line[i] == ';':
                    i += 1
                if text in ("S0;", ""):
                    output.append("S0;")
                else:
                    output.append("S" + ",".join(str(ord(c)) for c in text) + ",0;")
            elif not line[i].isspace():
                start = i
                while i < len(line) and not line[i].isspace():
                    i += 1
                output.append(line[start:i])
            else:
                i += 1
        return " ".join(output)

    def save_changes(self):
        if not self.characters:
            return
        values = []
        for name in self.value_names:
            if name == self.first_name_key and not self.line_by_line:
                current_data = self.parse_line(self.characters[self.current_character_index])
                values.append(f'"{current_data.get(name, "")}";')
                continue
            widget = self.value_entries[name]
            if self.value_types[name] == "Bool":
                values.append("1" if widget.isChecked() else "0")
            elif self.value_types[name] == "BoolString":
                values.append(f'"{self.bool_string_values[name][1] if widget.isChecked() else self.bool_string_values[name][0]}"')
            elif self.value_types[name] == "Integer":
                values.append(widget.text())
            else:
                values.append(f'"{widget.text()}";')
        self.characters[self.current_character_index] = " ".join(values) + " "
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Encoded Save File (*.glkdata)"
        )
        if not file_path:
            return
        modified_characters = [line if line.endswith(" ") else line + " " for line in self.characters]
        if self.is_encoded:
            modified_characters = [self.encode_glkdata_line(line).rstrip() + " " for line in modified_characters]
        with open(file_path, "w") as f:
            f.writelines(self.header_lines)
            f.write("\n".join(modified_characters) + "\n")
        QMessageBox.information(self, "Save Editor", "Changes saved successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)
    editor = SaveEditor()
    editor.show()
    QTimer.singleShot(100, editor.load_save)
    sys.exit(app.exec())
