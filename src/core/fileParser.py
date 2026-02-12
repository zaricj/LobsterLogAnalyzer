from ast import List
from PySide6.QtCore import Signal, QThread, Slot, QObject, QRunnable
import re
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from app import MainWindow


class RegexCompilerSignals(QObject):
    pass


class RegexCompilerWorker(QRunnable):
    """Worker thread for managing regex stuff"""

    def __init__(self, main_window: 'MainWindow'):
        super().__init__()
        self.main_window = main_window

    def run():
        pass

    def compile_regex(self, pattern: str):
        """Compiles regex string to a pattern object

        Args:
            pattern (str): The regex string to compile

        Returns:
            Pattern[AnyStr@compile]: Regex pattern object
        """
        return re.compile(pattern)

    def compile_regex_dictionary(self, pattern_dict: dict):
        return {
            name: re.compile(pattern, re.MULTILINE | re.DOTALL)
            for name, pattern in pattern_dict.items()
        }


class FileParserSignals(QObject):
    # progress_updated = Signal(int, str)
    # parsing_complete = Signal(list, dict)
    output_text_edit_append = Signal(str)


class FileParserWorker(QRunnable):
    """Worker thread for log parsing"""

    def __init__(self, main_window: 'MainWindow', log_files: list[Path] = None, patterns: list[str] = None):
        super().__init__()
        self.log_files = log_files
        self.patterns = patterns
        self.main_window = main_window
        self.ui = main_window.ui
        self.signals = FileParserSignals()
        self.setAutoDelete(True)

    def run(self):
        self.test()

    def test(self) -> None:
        for file in self.log_files:
            dict_obj: dict = self.read_file_line_by_line(file)

            # Read dictionary
            for key, value in dict_obj.items():
                output_line: str = f"{key}: {value}"
                self.signals.output_text_edit_append.emit(output_line)

    @Slot(str)
    def read_file(self, file: Path) -> str:
        with open(file, "r") as f:
            content = f.read()
        return content

    @Slot(str)
    def read_file_line_by_line(self, file: Path) -> dict:
        try:
            lines_dict: dict = {}
            try:
                with open(file, "r") as f:
                    lines = f.readlines()  # Read lines

                    for index, line in enumerate(lines, 0):
                        lines_dict[index] = line
            except FileNotFoundError:
                self.signals.output_text_edit_append.emit(
                    f"File not found: {file}")

            return lines_dict
        except Exception as e:
            message = f"An exception of type {type(e).__name__} occurred. Arguments: {e.args!r}"
            self.signals.output_text_edit_append.emit(message)
