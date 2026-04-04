from pathlib import Path
import json
import re
import csv
import xlsxwriter

# ========== Load & Compile Patterns ==========

def load_patterns_json(filepath: Path) -> dict[str, str]:
    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


def compile_regex(pattern: str, flags=0):
    return re.compile(pattern, flags)


def compile_regex_patterns(category_config: dict):
    """Compile base header + patterns for one category"""
    compiled = {}
    compiled["base"] = {name: re.compile(p) for name, p in category_config.get("base", {}).items()}
    compiled["patterns"] = {name: re.compile(p, re.MULTILINE | re.DOTALL) 
                            for name, p in category_config.get("patterns", {}).items()}
    return compiled

# ========== Input validation and get files ==========

def validate_input(file: Path | str) -> bool:
    try:
        # First check if file is not None
        if not file:
            raise ValueError("No file provided for processing.")
        
        if isinstance(file, str):
            file = Path(file)
            
        # If not None, check if file exists
        if not file.exists():
            raise FileNotFoundError(f"The specified file '{file}' does not exist.")
        else:
            return True
    except Exception as ex:
        print(f"Input validation error: {ex}")
        return False


def get_files_in_folder(directory: Path, file_pattern: str = "*.log") -> list[Path]:
    """Get files from a directory, of specific type

    Args:
        directory (Path): Path to the folder that contains files
        file_pattern (str, optional): Only get files that match this pattern. Defaults to "*.log".

    Returns:
        list[Path]: List of found files in the directory.
    """
    if directory.is_dir() and directory.exists():
        return list(directory.glob(file_pattern))
    
# ========== Excel Conversion ==========

def convert_csv_to_excel(input_csv_file: Path, output_excel_file: Path):
    # Validate csv input file
    is_csv_valid = validate_input(input_csv_file)
    
    if is_csv_valid:
        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(str(output_excel_file))
        worksheet = workbook.add_worksheet()
        # Open the CSV file and read its contents using the csv module
        # Use newline="" so the csv module can handle newlines correctly
        with open(input_csv_file, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=";", quotechar='"')
            for row_idx, row in enumerate(reader):
                for col_idx, cell in enumerate(row):
                    worksheet.write(row_idx, col_idx, cell)
        workbook.close()
        print(f"Excel written: {output_excel_file}")
    else:
        print("Invalid input file. Please provide a valid CSV file path.")
