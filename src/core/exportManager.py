"""This file contains business logic for exporting the final results to a csv file which would be used for the table result display and also an conversion to an excel file."""
from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtGui import QPixmap
import pandas as pd


class ExportManagerSignals(QObject):
    """Signals for export manager."""
    statusbar_message = Signal(str, int)  # message, duration
    export_success = Signal(str, str, str, str) # Shows a custom QMessageBox -> (title: str, message: str, save_as_path: str, app_icon_path: str)
    # message_info = Signal(str, str) # QMessageBox Information -> (title, message)


class ExportManager(QRunnable):
    """Handles CSV and Excel export"""

    def __init__(self, app_icon_path: str):
        super().__init__()
        self.signals = ExportManagerSignals()
        self.app_icon_path = app_icon_path
        self.setAutoDelete(True)

    @Slot(pd.DataFrame, str, str)
    def export_to_csv(self, data: pd.DataFrame, save_as_path: str, delimiter: str = ';'):
        # Enhanced CSV export with proper encoding
        # Convert pandas DataFrame to CSV
        self.signals.statusbar_message.emit("Exporting table data to CSV...", 5000)
        data.to_csv(save_as_path, index=False)
        self.signals.export_success.emit("Success", "Table result successfully converted to CSV", save_as_path, self.app_icon_path)

    @Slot(pd.DataFrame, str)
    def export_to_excel(self, data: pd.DataFrame, save_as_path: str):
        # Excel export with formatting
        self.signals.statusbar_message.emit("Exporting table data to Excel...", 5000)
        sheet_name = "Result"
        with pd.ExcelWriter(save_as_path, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            max_row, max_col = data.shape
            column_settings = [{"header": col} for col in data.columns]
            worksheet.add_table(0, 0, max_row, max_col - 1, {
                "columns": column_settings,
                "style": "Table Style Medium 16",
                "name": f"{sheet_name[:30]}",
                "autofilter": True
            })
            worksheet.set_column(0, max_col - 1, 18)
        self.signals.export_success.emit("Success", "Table result successfully converted to Excel", save_as_path, self.app_icon_path)