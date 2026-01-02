from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QDialog)

from PySide6.QtGui import QIcon, QCloseEvent, QGuiApplication, QAction
from PySide6.QtCore import (
    Qt,
    QFile,
    QTextStream,
    QIODevice,
    QSettings,
    QThreadPool
)

from gui.ui.main.LobsterGeneralLogViewer_ui import Ui_MainWindow
from utils.UIMixinUtility import Mixin

# ----------------------------
# Constants
# ----------------------------I
ROOT_DIR = Path(__file__).parent
GUI_PATTERN_DIRECTORY: Path = ROOT_DIR / "patterns"
GUI_PATTERN_FILE_PATH: Path = GUI_PATTERN_DIRECTORY / "patterns.json"

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

# ----------------------------
# Entrypoint
# ----------------------------
class MainWindow(QMainWindow, Mixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.thread_pool = QThreadPool() # Thread pool
        self.initialize_ui_all() # From Mixin class
        self.ui_state_manager.initial_ui_state_on_start()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())