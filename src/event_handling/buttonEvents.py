import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import MainWindow
    
class ButtonEventHandler:
    def __init__(self, main_window: 'MainWindow'):
        self.main_window = main_window
        self.ui = main_window.ui
        
    def connect_signals(self):
        """Connect all button events to their handlers."""
        # Browse folder button
        self.ui.button_browse_folder.clicked.connect(
            lambda: self.main_window.helper.browse_folder_helper("Browse folder", self.ui.input_browse_folder)
            )
        
        # Import CSV button
        self.ui.button_import_csv.clicked.connect(self.on_load_csv_file_for_table)
        
        # Clear table button
        self.ui.button_clear_table.clicked.connect(self.on_clear_table)
        
        # Parse files button - TODO: implement parsing logic
        self.ui.button_parse_files.clicked.connect(self.on_parse_files)
        
        # Export button - TODO: implement export logic
        # self.ui.button_export.clicked.connect(self.on_export_data)
        
        # Change directory button - TODO: implement directory change
        # self.ui.button_change_directory.clicked.connect(self.on_change_directory)
        
        # Refresh configuration button - TODO: implement config refresh
        # self.ui.button_refresh_configuration.clicked.connect(self.on_refresh_configuration)
        
    # ===== UI Events =====

    @Slot()
    def on_load_csv_file_for_table(self):
        """Load CSV file for table display."""
        try:
            file_path = self.main_window.helper.browse_file_helper_non_input(
                dialog_message="Select CSV file to display",
                file_extension_filter="CSV File (*.csv)"
            )

            if file_path:
                df = pd.read_csv(file_path)
                self.populate_results_table(df)
                self.main_window.ui_state_manager.set_table_widgets_disabled(False)
        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(self.main_window, "Exception loading CSV file", message)

    # Populate the Table Widget
    def populate_results_table(self, results: pd.DataFrame):
        """Display the DataFrame efficiently in a QTableView."""
        from gui.models import tableViewModel

        if results.empty:
            self.ui.table_view_result.setModel(None)
            return
        model = tableViewModel(results)
        self.ui.table_view_result.setModel(model)
        self.ui.table_view_result.resizeColumnsToContents()

    @Slot() 
    def on_clear_table(self):
        """Clear table data."""
        self.ui.table_view_result.setModel(None)
        self.ui.input_filter_table.clear()
        self.main_window.ui_state_manager.set_table_widgets_disabled(True)
        
    @Slot()
    def on_parse_files(self):
        pass