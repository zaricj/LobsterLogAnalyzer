"""Centralized signal connection management."""
from typing import TYPE_CHECKING
from core.exportManager import ExportManager

if TYPE_CHECKING:
    from app import MainWindow


class SignalConnector:
    """Manages signal connections for worker threads."""
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        self.ui = main_window.ui
        
    def connect_export_manager_signals(self, worker: ExportManager):
        """Connect signals for XML parsing operations."""
        worker.signals.statusbar_message.connect(self.main_window.handle_export_status_message)
        worker.signals.export_success.connect(self.main_window.handle_export_manager_success)