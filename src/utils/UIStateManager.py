"""Service for managing UI state and widget states."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import MainWindow


class UIStateManager:
    """
    Manages UI widget states (enabled/disabled, visible/hidden).
    Centralizes UI state management logic for better separation of concerns.
    """
    
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window
        self.ui = main_window.ui