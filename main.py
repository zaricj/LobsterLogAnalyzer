import csv
from pathlib import Path
from utility.utils import (
    get_csv_headers_from_sample,
    load_patterns_json,
    yield_event_block,
    compile_regex_patterns,
    get_files_in_folder,
    is_keyword_event,
    extract_event_fields
)

PATTERNS_CONFIG = Path("patterns/patterns.json")
FILE_PATTERN = "*.log"
LOGS_PATH = Path("logs")


def load_sql_config() -> tuple:
    """Load and compile SQL patterns. Returns (compiled_sql, header_regex)."""
    patterns_json = load_patterns_json(PATTERNS_CONFIG)
    compiled_sql = compile_regex_patterns(patterns_json["sql_exceptions"])
    header_regex = compiled_sql["base"]["header"]
    return compiled_sql, header_regex


def iter_sql_rows(log_files: list[Path], header_regex, compiled_sql, event_keyword: str) -> iter:
    """Yield one extracted row dict per SQL event across all log files."""
    for log_file in log_files:
        print(f"Processing file: '{log_file}'")
        for block in yield_event_block(log_file, header_regex):
            if is_keyword_event(event_keyword, block):
                yield extract_event_fields(block, compiled_sql)


def write_rows_to_csv(csv_output_file: Path, headers: list[str], rows: iter) -> int:
    """Write rows to a CSV file. Returns the number of lines written."""
    lines_written = 0
    with open(csv_output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=headers,
            delimiter=";",
            quotechar='"',
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            lines_written += 1
    return lines_written


def extract_and_write_to_csv(csv_output_file: str | Path):
    try:
        event_keyword = "sql"
        compiled_sql, header_regex = load_sql_config()
        log_files = get_files_in_folder(LOGS_PATH, FILE_PATTERN)

        print("Grabbing headers from sample file...")
        headers = get_csv_headers_from_sample(log_files[0], header_regex, compiled_sql, event_keyword)
        print(f"Starting to process {len(log_files)} files of type '{FILE_PATTERN}'")

        rows = iter_sql_rows(log_files, header_regex, compiled_sql, event_keyword)
        lines_written = write_rows_to_csv(csv_output_file, headers, rows)

        print(f"Task finished, results saved to '{csv_output_file}'\nTotal lines written: {lines_written}")
    except Exception as err:
        print(f"An error of type {type(err).__name__} occurred.\nError message: {str(err)}\nArguments: {err.args}")


# ========== MAIN ==========
if __name__ == "__main__":
    extract_and_write_to_csv(Path("CSV_Results.csv"))