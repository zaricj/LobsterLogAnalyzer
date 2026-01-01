from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot, QSettings

from gui.ui.main.LobsterGeneralLogViewer_ui import Ui_MainWindow
from gui.models.treeViewModel import DirectoryViewer
from gui.models.tableViewModel import ResultsTableWidget
from utils.UIStateManager import UIStateManager
from utils.helperUtility import HelperMethods


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
        self.initialize_views()
        self.initialize_utilities()    # Initialize utilities first
        self.initialize_handlers()     # Then handlers (which depend on utilities)
        self.initialize_ui_signals()   # Finally connect signals
        
    def initialize_handlers(self):
        """Initialize all specialized event handlers."""
        from event_handling.buttonEvents import ButtonEventHandler
        from event_handling.comboboxEvents import ComboBoxEventHandler
        
        self.button_handler = ButtonEventHandler(self)
        self.combobox_handler = ComboBoxEventHandler(self)
        
    def initialize_ui_signals(self):
        self.button_handler.connect_signals()
        self.combobox_handler.connect_signals()
        
    def initialize_utilities(self):
        self.helper = HelperMethods(self)
        self.ui_state_manager = UIStateManager(self)
    
    def initialize_views(self):
        self.dir_viewer = DirectoryViewer(self) # Init the tree view model object
        self.table_results = ResultsTableWidget(self)