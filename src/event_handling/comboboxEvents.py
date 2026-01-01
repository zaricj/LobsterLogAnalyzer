from math import comb
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QComboBox
from utils.patternHandler import PatternHandler
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from app import MainWindow
    
FILE_DIR = Path(__file__).resolve()
ROOT_DIR = FILE_DIR.parents[1] # src Folder
GUI_PATTERN_DIRECTORY: Path = ROOT_DIR / "patterns"
GUI_PATTERN_FILE_PATH: Path = GUI_PATTERN_DIRECTORY / "patterns.json"
    
# TODO Add another combobox for subkeys(?) and based on the choice of the main config if the main key has subkeys re-enable subkey combobox if it does not disabled it
# TODO also list available keys of main key in the output?
    
class ComboBoxEventHandler:
    def __init__(self, main_window: 'MainWindow'):
        self.main_window = main_window
        self.ui = main_window.ui
        # Load config handler object
        self.handler = PatternHandler(
            self,
            GUI_PATTERN_DIRECTORY,
            GUI_PATTERN_FILE_PATH
        )
        
        # Init combobox
        combobox = self.ui.combobox_configuration
        self.populate_patterns_combobox(combobox) # Fill the combobox with the available pattern configuration files
        
    def connect_signals(self):
        """Connect all combobox events to their handlers."""
        # Browse folder button
        self.ui.combobox_configuration.currentTextChanged.connect(self.load_pattern)
        
    # ===== UI Events =====
    
    def populate_patterns_combobox(self, combobox: QComboBox):
        patterns = self.handler.get_all_keys("exception_patterns")
        combobox.addItems(patterns)
        self.ui.text_edit_program_output.setText("Loaded pattern keys!")
        
    def load_pattern(self):
        pass