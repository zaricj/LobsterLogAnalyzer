from pathlib import Path
import csv
import xlsxwriter
from typing import List

def validate_inputs(file: Path) -> bool:
    try:
        # First check if file is not None
        if not file:
            raise ValueError("No file provided for processing.")
        # If not None, check if file exists
        elif not file.exists():
            raise FileNotFoundError(f"The specified file '{file}' does not exist.")
        else:
            return True
    except Exception as ex:
        print(f"Input validation error: {ex}")
        return False

# ---------- CSV Output ----------
def write_combined_csv(all_records, headers: List[str], output_csv_file: Path):
    with open(output_csv_file,"w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(headers)
        for row in all_records:
            writer.writerow(row)

    print(f"CSV written: {output_csv_file}")

# ---------- Excel Conversion ----------
def convert_csv_to_excel(input_csv_file: Path, output_excel_file: Path):
    # Validate csv input file
    is_csv_valid = validate_inputs(input_csv_file)
    
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