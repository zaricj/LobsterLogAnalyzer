from PySide6.QtCore import Slot
from PySide6.QtWidgets import QComboBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import MainWindow
    
    
class ComboBoxEventHandler:
    def __init__(self, main_window: 'MainWindow'):
        self.main_window = main_window
        self.ui = main_window.ui
        
        # Init combobox
        combobox = self.ui.combobox_configuration
        self.populate_patterns_combobox(combobox) # Fill the combobox with the available pattern configuration files
        
    def connect_signals(self):
        """Connect all combobox events to their handlers."""
        self.ui.combobox_configuration.currentTextChanged.connect(self.load_pattern)
        
    # ===== UI Events =====
    
    def populate_patterns_combobox(self, combobox: QComboBox):
        profiles = self.main_window.log_pattern_handler.get("profiles")
        if isinstance(profiles, dict) and profiles:
            default_profile = self.main_window.log_pattern_handler.get("default_profile")
            combobox.clear()
            combobox.addItems(sorted(profiles.keys()))
            if isinstance(default_profile, str) and default_profile in profiles:
                combobox.setCurrentText(default_profile)
            selected_profile = combobox.currentText()
            self.ui.text_edit_program_output.setText(
                f"Loaded pattern profiles: {', '.join(sorted(profiles.keys()))}\n"
                f"Selected profile: {selected_profile}"
            )
        else:
            self.ui.text_edit_program_output.setText(
                "No parser profiles found under 'profiles' in log_patterns.json."
            )
            
    @Slot(str)
    def load_pattern(self, profile_name: str) -> None:
        self.ui.statusbar.showMessage(f"Selected parser profile: {profile_name}", 5000)
