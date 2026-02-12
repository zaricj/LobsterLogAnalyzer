from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING, Self
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog,
    QSplitter)

from PySide6.QtGui import QIcon, QCloseEvent, QGuiApplication, QAction, QPixmap
from PySide6.QtCore import (
    Qt,
    QFile,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool
)

from gui.LobsterGeneralLogViewer_ui import Ui_MainWindow
from gui.utils.UIMixinUtility import Mixin

# ----------------------------
# Constants
# ----------------------------
ROOT_DIR = Path(__file__).parent
APP_ICON: Path = ROOT_DIR / "gui" / "assets" / "images" / "app-icon.png"

# Application versioning and metadata
APP_VERSION: str = "v0.0.1"
APP_NAME: str = "LobsterLogReportViewer"
AUTHOR: str = "Jovan"

# ----------------------------
# Helpers for window state
# ----------------------------
def save_window_state(window: QMainWindow, settings: QSettings):
    settings.setValue("geometry", window.saveGeometry())
    settings.setValue("windowState", window.saveState())

def restore_window_state(window: QMainWindow, settings: QSettings):
    geometry = settings.value("geometry")
    if geometry:
        window.restoreGeometry(geometry)
    state = settings.value("windowState")
    if state:
        window.restoreState(state)

    # Clamp window into current screen space
    screen = QGuiApplication.primaryScreen()
    available = screen.availableGeometry()
    win_geom = window.frameGeometry()

    if not available.contains(win_geom, proper=False):
        window.resize(
            min(win_geom.width(), available.width()),
            min(win_geom.height(), available.height())
        )
        window.move(
            max(available.left(), min(win_geom.left(), available.right() - window.width())),
            max(available.top(), min(win_geom.top(), available.bottom() - window.height()))
        )
        
def save_splitter_state(splitter: QSplitter, settings: QSettings, key: str = "splitterState"):
    settings.setValue(key, splitter.saveState())

def restore_splitter_state(splitter: QSplitter, settings: QSettings, key: str = "splitterState"):
    state = settings.value(key)
    if state:
        splitter.restoreState(state)
        
def initialize_theme(parent: Self, theme_file_path: str | Path, settings: QSettings, key: str = "appAppearanceMode"):
    try:
        file = QFile(theme_file_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            parent.setStyleSheet(stylesheet)
        file.close()
        save_app_theme(theme_file_path, settings)
    except Exception as ex:
        QMessageBox.critical(parent, "Theme load error", f"Failed to load theme: {str(ex)}")
        
def save_app_theme(theme_file_path: Path | str, settings: QSettings):
    settings.setValue("appAppearanceMode", theme_file_path)

# ----------------------------
# Entrypoint
# ----------------------------
class MainWindow(QMainWindow, Mixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Init directories
        self.root_dir = Path(__file__).parent
        self.config_dir: Path = self.root_dir / "config"
        self.log_pattern_config: Path = self.config_dir / "log_patterns.json"
        self.gui_settings_config: Path = self.config_dir / "gui_settings.json"
        
        self.dark_appearance_file_path: Path = self.root_dir / "gui" / "assets" / "styles" / "dark.qss" 
        self.light_appearance_file_path: Path = self.root_dir / "gui" / "assets" / "styles" / "light.qss" 
        
        # Application settings
        self.settings = QSettings("Jovan", "LobsterLogReporterApp")
        
        self.app_icon: str = APP_ICON.__str__()
        self.thread_pool: QThreadPool = QThreadPool() # Thread pool
        
        self.initialize_ui_all() # From Mixin class
        self.ui_state_manager.initial_ui_state_on_start()
        
        # Load initial application's settings
        self.load_app_settings()
        
    def load_app_settings(self) -> None:
        """Load application settings from QSettings."""
        # Restore geometry safely
        restore_window_state(self, self.settings)
        restore_splitter_state(self.ui.splitterTop, self.settings)
        # Initialize theme/style for application
        appearance_mode = self.settings.value("appAppearanceMode", str(self.dark_appearance_file_path))
        initialize_theme(self, appearance_mode, self.settings)
        self.ui.statusbar.showMessage("Application settings loaded.", 5000) # Shows message in statusbar
        
    # Helper method to save apps settings in a more DRY way
    def save_app_settings(self) -> None:
        """Save application settings to QSettings."""
        save_window_state(self, self.settings) # Save windows location and state
        save_splitter_state(self.ui.splitterTop, self.settings)
        self.settings.sync()  # optional: force write to disk
        
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle application close event to save settings."""
        self.save_app_settings()
        event.accept()  # Accept the event to close the application
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
