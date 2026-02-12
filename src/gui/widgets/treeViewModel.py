from PySide6.QtWidgets import QFileSystemModel, QLineEdit
from PySide6.QtCore import QModelIndex, QStandardPaths, Slot

from typing import TYPE_CHECKING
from pathlib import Path

from gui.thread_worker import Worker

if TYPE_CHECKING:
    from app import MainWindow

class DirectoryViewer():
    PREVIEW_MAX_BYTES = 256 * 1024

    def __init__(self, main_window: "MainWindow", start_path=None):
        self.main_window = main_window
        self.ui = main_window.ui
        self.start_path = start_path
        self._active_preview_worker: Worker | None = None
        self._pending_preview_path: str | None = None
        
        # 1. Setup the Model
        self.model = QFileSystemModel()
        
        # Set the root path for the model
        if self.start_path is None:
            # Default to the user's home directory if no path is provided
            # You can specify a starting path, e.g., 'C:/' on Windows or '/home/user/' on Linux
            # QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
            self.start_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
        else:
            self.start_path = str(self.start_path)

        # Set the root path on the model
        self.model.setRootPath(self.start_path)

        # 2. Setup the View
        self.ui.treeview_directory_view.setModel(self.model)
        
        # Set the view's root index to display the contents of the starting path
        # If you want to show the full drive structure, setRootPath is enough, 
        # but to limit the view to a specific folder's contents, set setRootIndex.
        root_index = self.model.index(self.start_path)
        self.ui.treeview_directory_view.setRootIndex(root_index)

        # Optional: Configure the view appearance
        self.ui.treeview_directory_view.setSortingEnabled(True)
        self.ui.treeview_directory_view.setHeaderHidden(False)
        
        # Optionally hide columns you don't need (e.g., size, type, date)
        # 0: Name, 1: Size, 2: Type, 3: Date Modified
        self.ui.treeview_directory_view.setColumnHidden(1, False) # Show Size
        self.ui.treeview_directory_view.setColumnHidden(2, True) # Hide Type
        self.ui.treeview_directory_view.setColumnHidden(3, False) # Hide Date Modified
        
        # Expand column 'Name'
        self.ui.treeview_directory_view.setColumnWidth(0, 200)
        
        # Connect the selection signal to a handler
        self.ui.treeview_directory_view.clicked.connect(self.on_item_clicked)
        
    def check_if_file_or_folder(self, path: str) -> str:
        """
        Checks if the given path is a file or folder.
        Returns "file", "folder", or "not found".
        """
        p = Path(path)
        if p.is_file():
            return "file"
        elif p.is_dir():
            return "folder"
        else:
            return "not found"
    
    def set_root_path(self, path: str):
        """
        Sets the root path for the directory viewer to display the contents of the given path.
        """
        self.model.setRootPath(path)
        root_index = self.model.index(path)
        self.ui.treeview_directory_view.setRootIndex(root_index)
        
    def on_item_clicked(self, index: QModelIndex):
        """
        Handles an item being clicked in the QTreeView.
        """
        # Get the absolute file path from the model for the given index
        file_path: str = self.model.filePath(index)
        # Init the line edit where to set the path
        line_edit: QLineEdit = self.ui.input_browse_folder
        check: str = self.check_if_file_or_folder(file_path)
    
        if check == "folder":
            self.set_folder_path(line_edit, file_path) # Set file path in the line edit
        elif check == "file":
            self.load_file_preview(file_path)
        else:
            self.ui.text_edit_log_preview.setPlainText(f"Path not found:\n{file_path}")
            self.ui.statusbar.showMessage("Unable to load selected path.", 5000)

    def load_file_preview(self, file_path: str) -> None:
        self._pending_preview_path = file_path
        self.ui.text_edit_log_preview.setPlainText(f"Loading file preview...\n{file_path}")

        worker = Worker(self.read_file_preview_content, file_path, self.PREVIEW_MAX_BYTES)
        worker.signals.result.connect(self.on_file_preview_result)
        worker.signals.error.connect(self.on_file_preview_error)
        worker.signals.finished.connect(self.on_file_preview_finished)
        self._active_preview_worker = worker
        self.main_window.thread_pool.start(worker)
        
    def set_folder_path(self, line_edit: QLineEdit, text_to_display: str = None):
        """
        Sets the selected item's path into the provided QLineEdit.
        """
        line_edit.setText(text_to_display)

    @staticmethod
    def read_file_preview_content(file_path: str, max_bytes: int) -> dict:
        file = Path(file_path)
        with file.open("rb") as handle:
            payload = handle.read(max_bytes + 1)

        is_truncated = len(payload) > max_bytes
        if is_truncated:
            payload = payload[:max_bytes]

        text = payload.decode("utf-8", errors="replace")
        return {
            "path": str(file),
            "content": text,
            "truncated": is_truncated,
        }

    @Slot(object)
    def on_file_preview_result(self, result: object) -> None:
        if not isinstance(result, dict):
            self.ui.text_edit_log_preview.setPlainText("Failed to render preview.")
            return

        path = str(result.get("path", ""))
        if not path:
            return

        preview_content = str(result.get("content", ""))
        is_truncated = bool(result.get("truncated", False))

        if is_truncated:
            preview_content += "\n\n[Preview truncated to first 256KB]"

        self.ui.text_edit_log_preview.setPlainText(preview_content)
        self.ui.statusbar.showMessage(f"Loaded preview: {path}", 5000)

    @Slot(tuple)
    def on_file_preview_error(self, error_data: tuple) -> None:
        _exctype, value, _traceback_text = error_data
        path = self._pending_preview_path or ""
        self.ui.text_edit_log_preview.setPlainText(
            f"Failed to load file preview:\n{path}\n\n{value}"
        )
        self.ui.statusbar.showMessage("File preview failed to load.", 5000)

    @Slot()
    def on_file_preview_finished(self) -> None:
        self._active_preview_worker = None
