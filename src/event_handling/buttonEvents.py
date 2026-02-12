from ast import Dict, List
import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidget, QTextEdit
from typing import TYPE_CHECKING
from pathlib import Path

from gui.models.tableViewModel import ResultsTableWidget
from core.exportManager import ExportManager
from core.fileParser import FileParserWorker


if TYPE_CHECKING:
    from app import MainWindow


class ButtonEventHandler:
    def __init__(self, main_window: 'MainWindow'):
        self.main_window = main_window
        self.ui = main_window.ui
        self.app_icon_path = self.main_window.app_icon

    def connect_signals(self):
        """Connect all button events to their handlers."""
        # Browse folder button
        self.ui.button_browse_folder.clicked.connect(
            lambda: self.main_window.helper.browse_folder_helper(
                "Browse folder", self.ui.input_browse_folder)
        )

        # Import CSV button
        self.ui.button_import_csv.clicked.connect(
            self.on_load_csv_file_for_table)

        # Clear table button
        self.ui.button_clear_table.clicked.connect(self.on_clear_table)

        # Parse files button - TODO: implement parsing logic --- STARTS THREAD
        self.ui.button_parse_files.clicked.connect(self.on_parse_files)

        # Export button - TODO: implement export logic
        self.ui.button_export.clicked.connect(self.on_export_data)

        # Pattern config info button
        self.ui.button_pattern_configuration_info.clicked.connect(
            self.on_pattern_config_info)

        # Refresh configuration button - TODO: implement config refresh
        # self.ui.button_refresh_configuration.clicked.connect(self.on_refresh_configuration)

    # ===== UI Events =====

    @Slot()
    def on_pattern_config_info(self) -> None:
        """Event of the button for the configuration pattern information
        """
        program_output: QTextEdit = self.ui.text_edit_program_output
        combobox_text: str = self.ui.combobox_configuration.currentText()
        current_combobox_data: dict | str = self.main_window.pattern_handler.get(
            combobox_text)

        if len(current_combobox_data) != 0:
            # Print to program output window
            if isinstance(current_combobox_data, dict):
                program_output.setText("Key\tValue")
                for key, value in current_combobox_data.items():
                    program_output.append(f"{key}   ----->   {value}")
            elif isinstance(current_combobox_data, str):
                program_output.setText(
                    f"Config value: {current_combobox_data}")
            else:
                program_output.setText(
                    "No data available or unsupported type.")

    @Slot()
    def on_load_csv_file_for_table(self) -> None:
        """Load CSV file for table display."""
        try:

            file_path = self.main_window.helper.browse_file_helper_non_input(
                dialog_message="Select CSV file to display",
                file_extension_filter="CSV File (*.csv)")

            if file_path:
                df = pd.read_csv(file_path)
                self.populate_results_table(df)
                widgets: List = [self.ui.button_clear_table, self.ui.button_export,
                                 self.ui.radiobutton_csv, self.ui.radiobutton_excel]
                self.main_window.ui_state_manager.enable_widgets(widgets)
                self.ui.statusbar.showMessage(
                    f"Loaded CSV file: {file_path}", 10000)

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception loading CSV file", message)

    @Slot()
    def on_parse_files(self) -> None:
        log_file = [Path(r"C:\Users\Jovan\Downloads\sample.log")]

        file_parser = FileParserWorker(self.main_window, log_file, None)
        self.main_window.signal_connector.connect_file_parser_worker(
            file_parser)
        self.main_window.thread_pool.start(file_parser)

    # === Table Widget Events ===

    # Populate the Table Widget

    @Slot(pd.DataFrame)
    def populate_results_table(self, data: pd.DataFrame) -> None:
        """Display the DataFrame efficiently in a QTableView."""
        try:
            from gui.models.tableViewModel import ResultsTableWidget

            if data.empty:
                self.ui.table_view_result.setModel(None)
                return

            model = ResultsTableWidget(data)
            self.ui.table_view_result.setModel(model)
            self.ui.table_view_result.resizeColumnsToContents()

        except Exception as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments: {ex.args!r}"
            QMessageBox.critical(
                self.main_window, "Exception loading CSV file", message)

    @Slot()
    def on_clear_table(self) -> None:
        """Clear table data."""
        self.ui.table_view_result.setModel(None)
        self.ui.input_filter_table.clear()
        widgets: List = [self.ui.button_clear_table, self.ui.button_export,
                         self.ui.radiobutton_csv, self.ui.radiobutton_excel]
        # Disable all widgets which are relevant for the Table widget
        self.main_window.ui_state_manager.disable_widgets(widgets)
        # Shows message in statusbar for 5 seconds
        self.ui.statusbar.showMessage("Cleared table data.", 5000)

    # ============================================================ #

    def on_export_data(self) -> None:
        try:
            model = self.ui.table_view_result.model()

            if model is None:
                QMessageBox.warning(
                    self.main_window, "Export", "No data to export.")
                return

            if not isinstance(model, ResultsTableWidget):
                QMessageBox.warning(self.main_window, "Export",
                                    "Unexpected table model type.")
                return

            df: pd.DataFrame = model.dataframe.copy()  # Dataframe

            csv_checked = self.ui.radiobutton_csv.isChecked()
            excel_checked = self.ui.radiobutton_excel.isChecked()

            if csv_checked:
                save_as = self.main_window.helper.browse_save_file_as_helper(
                    dialog_message="Save CSV file",
                    file_extension_filter="CSV File (*.csv)",
                    statusbar_widget=self.ui.statusbar)
                if not save_as:
                    return  # User cancelled the save dialog
                else:
                    exporter = ExportManager(self.main_window)
                    self.main_window.signal_connector.connect_export_manager_signals(
                        exporter)
                    exporter.export_to_csv(df, save_as, ",")
                    self.main_window.thread_pool.start(exporter)

            elif excel_checked:
                save_as = self.main_window.helper.browse_save_file_as_helper(
                    dialog_message="Save Excel file",
                    file_extension_filter="Excel File (*.xlsx)",
                    statusbar_widget=self.ui.statusbar)
                if not save_as:
                    return  # User cancelled the save dialog
                else:
                    exporter = ExportManager(self.main_window)
                    self.main_window.signal_connector.connect_export_manager_signals(
                        exporter)
                    exporter.export_to_excel(df, save_as)
                    self.main_window.thread_pool.start(exporter)
            else:
                QMessageBox.warning(self.main_window, "Export",
                                    "Please select CSV or Excel.")

        except Exception as ex:
            QMessageBox.critical(
                self.main_window,
                "Export Error",
                f"{type(ex).__name__}: {ex}"
            )
