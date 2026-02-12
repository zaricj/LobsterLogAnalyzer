from PySide6.QtGui import QAction
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import MainWindow

class MenuBarHandler:
    def __init__(self, main_window: 'MainWindow'):
        self.main_window = main_window
        self.settings = main_window.settings
        self.ui = main_window.ui
        
    def connect_signals(self) -> None:
        """Connect all menu bar actions for the  app"""
        self.ui.actionLight.triggered.connect(lambda: self.toggle_app_appearance(self.ui.actionLight.text().lower()))
        self.ui.actionDark.triggered.connect(lambda: self.toggle_app_appearance(self.ui.actionDark.text().lower()))
    
    @Slot()
    def toggle_app_appearance(self, appearance: str) -> None:
        """Toggle between light and dark appearance via the menu bar"""
        from app import initialize_theme
        
        action_light = self.ui.actionLight
        action_dark = self.ui.actionDark
        self._handle_appearance_check_state(appearance, action_light, action_dark)
        
        # Check which one is active and apply theme
        light_checked = action_light.isChecked()
        dark_checked = action_dark.isChecked()
        
        if dark_checked:
            initialize_theme(
                self.main_window,
                self.main_window.dark_appearance_file_path,
                self.settings,
            )
        if light_checked:
            initialize_theme(
                self.main_window,
                self.main_window.light_appearance_file_path,
                self.settings,
            )
        
    def _handle_appearance_check_state(self, appearance: str , action_light: QAction, action_dark: QAction) -> None:
        """Handle check state of the menu button in settings > appearance

        Args:
            appearance (str) The appearance type, light or dark.
            action_light (QAction) Check state of action that toggles the light appearance for the app 
            action_dark (QAction) Check state of action that toggles the dark appearance for the app
        """
        
        if appearance == "dark":
            # Check state
            action_dark.setChecked(True)
            action_light.setChecked(False)
            return
        if appearance == "light":
            action_dark.setChecked(False)
            action_light.setChecked(True)
            return
