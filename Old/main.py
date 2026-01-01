import re

from utility.utils import (
    load_patterns_json,
    compile_regex,
    compile_regex_dict,
    read_log_file,
    clean_block
)

from utility.csv_and_excel_writer import (
    write_combined_csv,
    convert_csv_to_excel
)

from pathlib import Path
from collections import Counter
from datetime import datetime

# ---------- Parsing Logic ----------
def analyze_log(logfile: Path,
                entry_pattern,
                sql_pattern,
                param_pattern,
                caused_pattern,
                ignore_pattern,
                exception_patterns):
    
    log_data = read_log_file(logfile)
    matches = entry_pattern.finditer(log_data)
    exception_counter = Counter()
    records = []

    for match in matches:
        time = match.group("time")
        time = f"{logfile.stem.strip('_error').replace('_', '-')} {time}"

        source = match.group("source")
        block = match.group("error_block").strip()
        block = clean_block(block, ignore_pattern)

        # Extract SQL
        sql_match = sql_pattern.search(block)
        sql_stmt = sql_match.group("sql").strip() if sql_match else ""

        # Detect exception type with patterns.json definitions
        exc_type = "No exception found"
        for key, regex in exception_patterns.items():
            if regex.search(block):
                exc_type = key
                break

        # Extract params
        params = param_pattern.findall(block)
        param_data = "; ".join(
            [f"{p}='{v}'" for p, v in params]) if params else ""

        # Caused by
        cause_match = caused_pattern.search(block)
        caused_by = cause_match.group("cause").strip() if cause_match else ""

        # fallback summary
        summary_line = block.splitlines()[0] if block else ""
        final_sql = sql_stmt or summary_line

        # Store row
        records.append((time, source, final_sql, exc_type, param_data, caused_by))
        exception_counter[exc_type] += 1

    return records, exception_counter

def print_summary(counter: Counter):
    print("\n=== Exception Summary ===")
    for exc, count in counter.most_common():
        print(f"{exc:40} {count}")


# ---------- MAIN ----------
if __name__ == "__main__":
    
    # Load patterns.json
    patterns = load_patterns_json(Path("patterns/patterns.json"))
    print(patterns)
    
    # Compile patterns
    entry_pattern = compile_regex(patterns["entry_header_pattern"], re.DOTALL)
    sql_pattern = compile_regex(patterns["sql_statement_pattern"], re.DOTALL)
    param_pattern = compile_regex(patterns["param_pattern"])
    caused_pattern = compile_regex(patterns["caused_by_pattern"], re.MULTILINE)
    ignore_pattern = compile_regex(patterns["ignore_stacktrace_pattern"], re.MULTILINE)
    
    # Compile exception sub-dict
    exception_patterns = compile_regex_dict(patterns["exception_patterns"])
    
    # Find logs
    log_dir = Path("logs")
    log_files = list(log_dir.glob("*.log"))
    
    if not log_files:
        print("No log files found in /logs")
        raise SystemExit
    print(f"Found {len(log_files)} log files.\n")
    
    all_records = []
    global_counter = Counter()
    
    for log_file in log_files:
        print(f"Processing: {log_file.name}")
        records, counter = analyze_log(
            log_file,
            entry_pattern,
            sql_pattern,
            param_pattern,
            caused_pattern,
            ignore_pattern,
            exception_patterns
        )
        
        all_records.extend(records)
        global_counter.update(counter)
        
    # CSV filename
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    output_dir = Path("CSVOutput")
    output_dir.mkdir(exist_ok=True)
    output_csv = output_dir / f"combined_report_{timestamp}.csv"
    
    headers = ["Time", "Source", "Error Details", "Exception Type", "Parameters", "Caused By"]
    
    write_combined_csv(all_records, headers, output_csv)
    convert_csv_to_excel(output_csv, output_csv.with_suffix('.xlsx'))
    print_summary(global_counter)
    
    print(f"\nDone. Parsed {len(log_files)} log files with {len(all_records)} total entries.")
