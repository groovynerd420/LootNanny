from decimal import Decimal
import os

from PyQt5.QtWidgets import QFileDialog, QFormLayout, QHeaderView, QTabWidget, QCheckBox, QGridLayout, QComboBox, QLineEdit, QLabel, QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem

from data.weapons import ALL_WEAPONS
from data.attachments import ALL_ATTACHMENTS
from data.creatures import ALL_CREATURES


class ConfigTab(QWidget):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app

        layout = QVBoxLayout()

        form_inputs = QFormLayout()
        # Add widgets to the layout

        # Chat Location
        self.chat_location = ""
        self.chat_location_text = QLineEdit()
        form_inputs.addRow("Chat Location:", self.chat_location_text)
        self.chat_location_text.editingFinished.connect(self.onChatLocationChanged)
        btn = QPushButton("Find File")
        form_inputs.addWidget(btn)
        btn.clicked.connect(self.open_files)

        # Creatue Configuration
        targetCreature = QComboBox()
        targetCreature.addItems(sorted(ALL_CREATURES))
        form_inputs.addRow("Mob:", targetCreature)

        self.character_name = QLineEdit()
        form_inputs.addRow("Character Name:", self.character_name)
        self.character_name.editingFinished.connect(self.onNameChanged)

        # Weapon Configuration
        self.weapon_option = QComboBox()
        self.weapon_option.addItems(sorted(ALL_WEAPONS))
        form_inputs.addRow("Weapon:", self.weapon_option)
        self.weapon_option.currentIndexChanged.connect(self.onWeaponChanged)

        self.amp_option = QComboBox()
        self.amp_option.addItems(["Unamped"] + sorted(ALL_ATTACHMENTS))
        form_inputs.addRow("Amplifier:", self.amp_option)
        self.amp_option.currentIndexChanged.connect(self.onAmpChanged)

        self.damage_enhancers = QLineEdit(text="0")
        form_inputs.addRow("Damage Enhancers:", self.damage_enhancers)
        self.damage_enhancers.editingFinished.connect(self.onEnhancersChanged)

        self.accuracy_enhancers = QLineEdit(text="0")
        form_inputs.addRow("Accuracy Enhancers:", self.accuracy_enhancers)

        # Calculated Configuration
        self.ammo_burn_text = QLineEdit(text="0", enabled=False)
        form_inputs.addRow("Ammo Burn:", self.ammo_burn_text)

        self.weapon_decay_text = QLineEdit(text="0.0", enabled=False)
        form_inputs.addRow("Tool Decay:", self.weapon_decay_text)

        # Screenshots
        self.screenshots_enabled = True
        self.screenshot_directory = "~/Documents/Globals/"
        self.screenshot_delay_ms = 500

        self.screenshots_checkbox = QCheckBox()
        self.screenshots_checkbox.setChecked(True)
        form_inputs.addRow("Take Screenshot On global/hof", self.screenshots_checkbox)

        self.screenshots_directory_text = QLineEdit(text="~/Documents/Globals/")
        form_inputs.addRow("Screenshot Directory:", self.screenshots_directory_text)

        self.screenshots_delay = QLineEdit(text="500")
        form_inputs.addRow("Screenshot Delay (ms):", self.screenshots_delay)

        # Set Layout
        layout.addLayout(form_inputs)

        self.setLayout(layout)

        if not os.path.exists(os.path.expanduser(self.screenshot_directory)):
            os.makedirs(os.path.expanduser(self.screenshot_directory))

    def open_files(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
        self.chat_location_text.setText(path[0])
        self.onChatLocationChanged()

    def recalculateWeaponFields(self):
        weapon = ALL_WEAPONS[self.app.combat_module.active_weapon]
        amp = ALL_ATTACHMENTS.get(self.app.combat_module.active_amp)
        ammo = weapon["ammo"] * (1 + (0.1 * self.app.combat_module.damage_enhancers))
        decay = weapon["decay"] * Decimal(1 + (0.1 * self.app.combat_module.damage_enhancers))
        if amp:
            ammo += amp["ammo"]
            decay += amp["decay"]
        self.ammo_burn_text.setText(str(int(ammo)))
        self.weapon_decay_text.setText(str(decay))

        self.app.combat_module.decay = decay
        self.app.combat_module.ammo_burn = ammo

        self.app.save_config()
        self.app.combat_module.update_active_run_cost()

    def load_from_config(self, config):
        self.damage_enhancers.setText(str(config["damage_enhancers"]))
        self.accuracy_enhancers.setText(str(config["accuracy_enhancers"]))
        self.weapon_option.setCurrentText(config["weapon"])
        self.amp_option.setCurrentText(config["amp"])
        self.character_name.setText(config.get("name", ""))

    def onWeaponChanged(self):
        self.app.combat_module.active_weapon = self.weapon_option.currentText()
        self.recalculateWeaponFields()

    def onAmpChanged(self):
        self.app.combat_module.active_amp = self.amp_option.currentText()
        self.recalculateWeaponFields()

    def onEnhancersChanged(self):
        self.app.combat_module.damage_enhancers = min(10, int(self.damage_enhancers.text()))
        self.recalculateWeaponFields()

    def onNameChanged(self):
        self.app.combat_module.active_character = self.character_name.text()
        self.app.save_config()

    def onChatLocationChanged(self):
        self.chat_location = self.chat_location_text.text()
        print(self.chat_location)
