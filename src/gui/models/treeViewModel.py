from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QTreeView, QPushButton, QLineEdit)
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import QDir, QModelIndex, QStandardPaths

from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from app import MainWindow

class DirectoryViewer():
    def __init__(self, main_window: "MainWindow", start_path=None):
        self.main_window = main_window
        self.ui = main_window.ui
        self.start_path = start_path
        
        # 1. Setup the Model
        self.model = QFileSystemModel()
        
        # Set the root path for the model
        if self.start_path is None:
            # Default to the user's home directory if no path is provided
            # You can specify a starting path, e.g., 'C:/' on Windows or '/home/user/' on Linux
            # QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
            self.start_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation)
        else:
            self.start_path = QDir.currentPath()

        # Set the root path on the model
        self.model.setRootPath(self.start_path)

        # 2. Setup the View
        self.ui.treeview_directory_view
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
        self.ui.treeview_directory_view.setColumnHidden(3, True) # Hide Date Modified
        
        # Connect the selection signal to a handler
        self.ui.treeview_directory_view.clicked.connect(self.on_item_clicked)
        
    def on_item_clicked(self, index: QModelIndex):
        """
        Handles an item being clicked in the QTreeView.
        """
        # Get the absolute file path from the model for the given index
        file_path: str = self.model.filePath(index)
        # Init the line edit where to set the path
        line_edit: QLineEdit = self.ui.input_browse_folder
        check: str = self.check_if_file_or_folder(file_path)
    
        if check == "folder": # Only print if folder for now
            # Set file path in the line edit underneath it
            self.set_item_path_in_line_edit(line_edit, file_path)
        
    def set_item_path_in_line_edit(self, line_edit: QLineEdit, text_to_display: str = None):
        """
        Sets the selected item's path into the provided QLineEdit.
        """
        line_edit.setText(text_to_display)
        
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