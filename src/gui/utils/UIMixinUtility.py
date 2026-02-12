from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot, QSettings

from gui.ui.main.LobsterGeneralLogViewer_ui import Ui_MainWindow
from gui.models.treeViewModel import DirectoryViewer
from gui.models.tableViewModel import ResultsTableWidget

# Path configuration (for pattern handler mainly)
FILE_DIR = Path(__file__).resolve()
ROOT_DIR = FILE_DIR.parents[1]  # src Folder
GUI_PATTERN_DIRECTORY: Path = ROOT_DIR / "patterns"
GUI_PATTERN_FILE_PATH: Path = GUI_PATTERN_DIRECTORY / "patterns.json"

class Mixin:
    """
    Mixin class that provides signal handling interface using specialized handlers.
    Delegates responsibilities to focused handler classes for better separation of concerns.
    """
    # Type hints for attributes accessed in this mixin
    ui: Ui_MainWindow
    # helper: 'HelperMethods'
    # ui_state_manager: 'UIStateManager'
    settings: 'QSettings'
    set_max_threads: int

    def initialize_ui_all(self):
        """Initialize all utilities, handlers, ui signals etc...
        """
        self.initialize_views()        # Initialize all the different views like Table and Tree
        self.initialize_utilities()    # Initialize utilities first
        self.initialize_handlers()     # Then handlers (which depend on utilities)
        self.initialize_handler_signals()   # Finally connect signals

    def initialize_handlers(self):
        """Initialize all specialized event handlers."""
        from event_handling.buttonEvents import ButtonEventHandler
        from event_handling.comboboxEvents import ComboBoxEventHandler
        from event_handling.lineEditEvents import LineEditHandler

        self.button_handler = ButtonEventHandler(self)
        self.combobox_handler = ComboBoxEventHandler(self)
        self.line_edit_handler = LineEditHandler(self)

    def initialize_handler_signals(self):
        self.button_handler.connect_signals()
        self.combobox_handler.connect_signals()
        self.line_edit_handler.connect_signals()

    def initialize_utilities(self):
        from utils.UIStateManager import UIStateManager
        from utils.helperUtility import HelperMethods
        from utils.patternHandler import PatternHandler

        self.helper = HelperMethods(self)
        self.ui_state_manager = UIStateManager(self)
        self.pattern_handler = PatternHandler(self,
                                              GUI_PATTERN_DIRECTORY,
                                              GUI_PATTERN_FILE_PATH)

    def initialize_views(self):
        # Init the tree view model object
        self.dir_viewer = DirectoryViewer(self)
        self.table_results = ResultsTableWidget(self)

